export class Time {
  constructor(private hour: number, private minute: number, private second: number) {
    if (!(Number.isInteger(hour) && 0 <= hour && hour < 24)) {
      throw new Error("Invalid hour value")
    } else if (!(Number.isInteger(minute) && 0 <= minute && minute < 60)) {
      throw new Error("Invalid minute value")
    } else if (!(Number.isInteger(second) && 0 <= second && second < 60)) {
      throw new Error("Invalid second value")
    }
  }

  public increase() {
    this.second = (this.second + 1) % 60
    this.minute = (this.minute + Number(!this.second)) % 60
    this.hour = (this.hour + Number(!this.minute && !this.second)) % 24
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
    return `${this.hour}:${this.minute}:${this.second}`
  }
}
