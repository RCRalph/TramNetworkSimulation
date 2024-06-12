<template>
  <v-footer>
    <v-row no-gutters>
      <v-col cols="4">
        <v-slider
          v-model="timeout"
          label="Timeout (ms)"
          step="1"
          min="1"
          max="1000"
          hide-details
        >
          <template v-slot:append>
            <v-text-field
              v-model="timeout"
              density="compact"
              style="width: 100px"
              type="number"
              variant="outlined"
              hide-details
            ></v-text-field>
          </template>
        </v-slider>
      </v-col>

      <v-col cols="4">
        <v-slider
          v-model="nodeBlocking"
          :min="1"
          :max="nodeChecking - 1"
          :readonly="props.disableChanges"
          label="Node blocking (s)"
          step="1"
          hide-details
        >
          <template v-slot:append>
            <v-text-field
              v-model="nodeBlocking"
              :min="1"
              :max="nodeChecking - 1"
              :disabled="props.disableChanges"
              density="compact"
              style="width: 100px"
              type="number"
              variant="outlined"
              hide-details
            ></v-text-field>
          </template>
        </v-slider>
      </v-col>

      <v-col cols="4">
        <v-slider
          v-model="nodeChecking"
          :min="nodeBlocking + 1"
          :max="60"
          :readonly="props.disableChanges"
          label="Node checking (s)"
          step="1"
          hide-details
        >
          <template v-slot:append>
            <v-text-field
              v-model="nodeChecking"
              :min="nodeBlocking + 1"
              :max="60"
              :disabled="props.disableChanges"
              density="compact"
              style="width: 100px"
              type="number"
              variant="outlined"
              hide-details
            ></v-text-field>
          </template>
        </v-slider>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script setup lang="ts">
const props = defineProps<{
  disableChanges: boolean
}>()

const timeout = defineModel<number>("timeout", {required: true})
const nodeBlocking = defineModel<number>("nodeBlocking", {required: true})
const nodeChecking = defineModel<number>("nodeChecking", {required: true})
</script>
