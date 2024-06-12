<template>
  <v-footer>
    <v-row no-gutters>
      <v-col cols="2">
        <div class="button-box">
          <v-btn
            :disabled="disabledButtons.start || props.loading"
            :loading="props.loading"
            text="Start"
            color="primary"
            @click="onStart"
          ></v-btn>

          <v-btn
            :disabled="disabledButtons.pause || props.loading"
            text="Pause"
            color="secondary"
            @click="onPause"
          ></v-btn>

          <v-btn
            :disabled="disabledButtons.reset || props.loading"
            text="Reset"
            color="red"
            @click="onReset"
          ></v-btn>
        </div>
      </v-col>

      <v-col
        cols="4"
        class="text-center text-capitalize"
      >
        Current time <br> {{ props.time.toString() }}
      </v-col>

      <v-col
        cols="4"
        class="text-center text-capitalize"
      >
        Elapsed time <br> {{ elapsedTime.toString() }}
      </v-col>

      <v-col cols="2">
        <v-select
          v-model="dayType"
          :items="props.dayTypes"
          label="Day type"
          variant="solo"
          density="comfortable"
          hide-details
        ></v-select>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script setup lang="ts">
import { Time } from "@classes/Time"
import { ref, watch } from "vue"

const props = defineProps<{
  time: Time,
  dayTypes: string[],
  loading: boolean
}>()

const emit = defineEmits<{
  (e: "reset"): void,
}>()

const running = defineModel<boolean>("running", {required: true})
const dayType = defineModel<string>("dayType", {required: true})

function useTimer() {
  let timer: NodeJS.Timeout | undefined = undefined

  let previousTime = 0

  let startTime = new Date()

  let elapsedTime = ref(new Time())

  function updateTime() {
    const elapsedSeconds = Math.floor((Number(new Date()) - Number(startTime) + previousTime) / 1000)

    while (elapsedSeconds > elapsedTime.value.seconds) {
      elapsedTime.value.advance(false)
    }
  }

  function startTimer() {
    if (timer) return

    startTime = new Date()
    timer = setInterval(updateTime, 10)
  }

  function stopTimer() {
    if (!timer) return

    updateTime()
    previousTime += Number(new Date()) - Number(startTime)

    clearInterval(timer)
    timer = undefined
  }

  function resetTimer() {
    stopTimer()
    elapsedTime.value = new Time()
    previousTime = 0
  }

  return {elapsedTime, startTimer, stopTimer, resetTimer}
}

function useButtons() {
  const disabledButtons = ref({
    start: false,
    pause: true,
    reset: true,
  })

  function onStart() {
    startTimer()
    running.value = true
    disabledButtons.value = {
      start: true,
      pause: false,
      reset: false,
    }
  }

  function onPause() {
    stopTimer()
    running.value = false
    disabledButtons.value = {
      start: false,
      pause: true,
      reset: false,
    }
  }

  function onReset() {
    resetTimer()
    running.value = false
    disabledButtons.value = {
      start: false,
      pause: true,
      reset: true,
    }

    emit("reset")
  }

  return {disabledButtons, onStart, onPause, onReset}
}

const {disabledButtons, onStart, onPause, onReset} = useButtons()
const {elapsedTime, startTimer, stopTimer, resetTimer} = useTimer()

watch(dayType, onReset)
</script>

<style scoped>
.button-box {
  display: flex;
  justify-content: left;
  align-items: center;
  height: 100%;
  gap: 10px;
}
</style>
