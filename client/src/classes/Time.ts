export class Time {
  public static readonly SECONDS_IN_DAY = 24 * 60 * 60

  constructor(private hour = 0, private minute = 0, private second = 0) {
    if (!(Number.isInteger(hour) && 0 <= hour && hour < 24)) {
      throw new Error("Invalid hour value")
    } else if (!(Number.isInteger(minute) && 0 <= minute && minute < 60)) {
      throw new Error("Invalid minute value")
    } else if (!(Number.isInteger(second) && 0 <= second && second < 60)) {
      throw new Error("Invalid second value")
    }
  }

  public advance(wrapTime = true) {
    this.second = (this.second + 1) % 60
    this.minute = (this.minute + Number(!this.second)) % 60

    const hourChange = Number(!this.minute && !this.second)
    if (wrapTime) {
      this.hour = (this.hour + hourChange) % 24
    } else {
      this.hour += hourChange
    }
  }

  public subtractMinute() {
    if (this.minute) {
      this.minute--
    } else {
      this.minute = 59
      this.hour = (this.hour - 1 + 24) % 24
    }
  }

  public equals(other: any, delay = 0) {
    return other instanceof Time && this.seconds + delay == other.seconds
  }

  public get seconds() {
    return (this.hour * 60 + this.minute) * 60 + this.second
  }

  public isLaterThan(other: Time) {
    return this.seconds > other.seconds
  }

  public clone() {
    return new Time(this.hour, this.minute, this.second)
  }

  public toString() {
    return [this.hour, this.minute, this.second]
      .map(item => String(item).padStart(2, "0"))
      .join(":")
  }
}
