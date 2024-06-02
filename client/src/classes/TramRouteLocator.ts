import { MoveVector } from "@classes/MoveVector"
import { LatLng } from "leaflet"

export interface TramRouteNode {
  distance: number
  coordinates: LatLng
}

export class TramRouteLocator {
  private static ROUTES: Record<number, Record<number, TramRouteNode[]>> = {}

  private currentTravelTime = 0

  constructor(
    private readonly startStop: number,
    private readonly endStop: number,
    private readonly totalTravelTime: number,
  ) {
    if (typeof TramRouteLocator.ROUTES[this.startStop] == "undefined") {
      throw new Error(`Invalid start stop ID: ${this.startStop}`)
    } else if (typeof TramRouteLocator.ROUTES[this.startStop][this.endStop] == "undefined") {
      throw new Error(`Invalid end stop ID: ${this.endStop}`)
    } else if (!(Number.isInteger(this.totalTravelTime) && this.totalTravelTime > 0)) {
      throw new Error(`Invalid travel time value: ${this.totalTravelTime}`)
    }
  }

  public static addRoute(startNode: number, endNode: number, nodes: TramRouteNode[]) {
    if (typeof TramRouteLocator.ROUTES[startNode] == "undefined") {
      TramRouteLocator.ROUTES[startNode] = {}
    }

    TramRouteLocator.ROUTES[startNode][endNode] = nodes
  }

  public get arrived() {
    return this.currentTravelTime == this.totalTravelTime
  }

  private get route() {
    return TramRouteLocator.ROUTES[this.startStop][this.endStop]
  }

  private get totalDistance() {
    return this.route[this.route.length - 1].distance
  }

  public getNewTramLocation() {
    const expectedDistance = (this.totalDistance / this.totalTravelTime) * this.currentTravelTime++
    const lastRouteNodeIndex = this.route.findLastIndex(item => expectedDistance >= item.distance)
    const segmentLength = this.route[lastRouteNodeIndex + 1].distance - this.route[lastRouteNodeIndex].distance

    return MoveVector
      .fromLatLng(this.route[lastRouteNodeIndex].coordinates, this.route[lastRouteNodeIndex + 1].coordinates)
      .scale((expectedDistance - this.route[lastRouteNodeIndex].distance) / segmentLength)
      .translate(this.route[lastRouteNodeIndex].coordinates)
  }
}
