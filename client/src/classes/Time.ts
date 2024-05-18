export class Time {
  constructor(private hour: number, private minute: number) {
    if (!(Number.isInteger(hour) && 0 <= hour && hour < 24)) {
      throw new Error("Invalid hour value")
    } else if (!(Number.isInteger(minute) && 0 <= minute && minute < 60)) {
      throw new Error("Invalid minute value")
    }
  }

  public addMinute() {
    this.minute = (this.minute + 1) % 60
    this.hour = (this.hour + Number(!this.minute)) % 24
  }

  public equals(other: any) {
    return other instanceof Time &&
      this.hour === other.hour &&
      this.minute === other.minute
  }

  public isLaterThan(other: Time) {
    return this.hour === other.hour ?
      this.minute > other.minute :
      this.hour > other.hour
  }

  public clone(): Time {
    return new Time(this.hour, this.minute)
  }
}
