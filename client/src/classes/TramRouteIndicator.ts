import { MoveVector } from "@classes/MoveVector"
import { LatLng } from "leaflet"

export interface TramRouteNode {
  distance: number
  coordinates: LatLng
}

export class TramRouteIndicator {
  private static ROUTES: Record<number, Record<number, TramRouteNode[]>> = {}

  private currentTravelTime = 0

  private moveVector: MoveVector = new MoveVector()

  constructor(
    private readonly startStop: number,
    private readonly endStop: number,
    private readonly totalTravelTime: number,
  ) {
    if (typeof TramRouteIndicator.ROUTES[this.startStop] == "undefined") {
      throw new Error(`Invalid start stop ID: ${this.startStop}`)
    } else if (typeof TramRouteIndicator.ROUTES[this.startStop][this.endStop] == "undefined") {
      throw new Error(`Invalid end stop ID: ${this.endStop}`)
    } else if (!(Number.isInteger(this.totalTravelTime) && this.totalTravelTime > 0)) {
      throw new Error(`Invalid travel time value: ${this.totalTravelTime}`)
    }

    this.moveVector = MoveVector.fromLatLng(
      this.getLocationForDistance(0),
      this.getLocationForDistance(this.velocity),
    )
  }

  public static addRoute(startNode: number, endNode: number, nodes: TramRouteNode[]) {
    if (typeof TramRouteIndicator.ROUTES[startNode] == "undefined") {
      TramRouteIndicator.ROUTES[startNode] = {}
    }

    TramRouteIndicator.ROUTES[startNode][endNode] = nodes
  }

  public get arrived() {
    return this.currentTravelTime == this.totalTravelTime
  }

  public get velocity() {
    return this.totalDistance / this.totalTravelTime
  }

  private get route() {
    return TramRouteIndicator.ROUTES[this.startStop][this.endStop]
  }

  private get totalDistance() {
    return this.route[this.route.length - 1].distance
  }

  private getRouteNodeIndex(distance: number) {
    return this.route.findLastIndex(item => distance >= item.distance)
  }

  private getLocationForDistance(distance: number) {
    const routeNodeIndex = this.getRouteNodeIndex(distance)

    if (routeNodeIndex == this.route.length - 1) {
      return this.route[this.route.length - 1].coordinates
    }

    const lastSegmentLength = this.route[routeNodeIndex + 1].distance - this.route[routeNodeIndex].distance

    return MoveVector
      .fromLatLng(this.route[routeNodeIndex].coordinates, this.route[routeNodeIndex + 1].coordinates)
      .scale((distance - this.route[routeNodeIndex].distance) / lastSegmentLength)
      .translate(this.route[routeNodeIndex].coordinates)
  }

  public getFutureRoute(seconds: number) {
    const currentDistance = this.velocity * this.currentTravelTime
    const currentRouteNodeIndex = this.getRouteNodeIndex(currentDistance)

    const futureDistance = this.velocity * (this.currentTravelTime + seconds)
    const futureRouteNodeIndex = this.getRouteNodeIndex(futureDistance)

    const result = [this.getLocationForDistance(currentDistance)]

    for (let i = currentRouteNodeIndex + 1; i <= futureRouteNodeIndex; i++) {
      result.push(this.route[i].coordinates)
    }

    if (futureRouteNodeIndex < this.route.length - 1) {
      result.push(this.getLocationForDistance(futureDistance))
    }

    return result
  }

  public getNewTramLocation() {
    const distance = this.velocity * this.currentTravelTime

    if (this.currentTravelTime) {
      this.moveVector = MoveVector.fromLatLng(
        this.getLocationForDistance(this.velocity * (this.currentTravelTime - 1)),
        this.getLocationForDistance(distance),
      )
    } else {
      this.moveVector = MoveVector.fromLatLng(
        this.getLocationForDistance(distance),
        this.getLocationForDistance(this.velocity * (this.currentTravelTime + 1)),
      )
    }

    this.currentTravelTime++

    return this.getLocationForDistance(distance)
  }

  public getTramRotation() {
    return this.moveVector.angle
  }
}
