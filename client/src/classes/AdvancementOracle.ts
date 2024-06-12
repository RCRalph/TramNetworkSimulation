import { TramPassage } from "@classes/TramPassage"
import { LatLng } from "leaflet"

export class AdvancementOracle {
  private tramsOnMap = new Set<TramPassage>()
  private occupiedNodes = new Map<string, TramPassage>()
  private previousRoutes = new Map<TramPassage, LatLng[]>()
  private tramsWaitingForRegistration = new Set<TramPassage>()

  private latLngKey(latlng: LatLng) {
    return `${Math.floor(latlng.lat * 10_000_000) / 10_000_000},${Math.floor(latlng.lng * 10_000_000) / 10_000_000}`
  }

  private addTramToMap(tram: TramPassage) {
    this.tramsOnMap.add(tram)
    this.occupiedNodes.set(this.latLngKey(tram.marker.getLatLng()), tram)
  }

  public registerTram(tram: TramPassage) {
    if (!this.occupiedNodes.has(this.latLngKey(tram.marker.getLatLng()))) {
      this.addTramToMap(tram)
    } else {
      this.tramsWaitingForRegistration.add(tram)
    }
  }

  public unregisterTram(tram: TramPassage) {
    if (!this.tramsOnMap.has(tram)) return

    this.tramsOnMap.delete(tram)

    for (const node of this.previousRoutes.get(tram) ?? []) {
      this.occupiedNodes.delete(this.latLngKey(node))
    }

    console.log(this.tramsOnMap, this.occupiedNodes)
  }

  private laysOnSegment(start: LatLng, end: LatLng, point: LatLng) {
    const epsilon = 1e-12
    const triangleArea = Math.abs(
      start.lng * (end.lat - point.lat) + end.lng * (point.lat - start.lat) + point.lng * (start.lat - end.lat),
    )

    return triangleArea <= epsilon &&
      Math.min(start.lat, end.lat) - epsilon <= point.lat && point.lat <= Math.max(start.lat, end.lat) + epsilon &&
      Math.min(start.lng, end.lng) - epsilon <= point.lng && point.lng <= Math.max(start.lng, end.lng) + epsilon
  }

  public canAdvance(tram: TramPassage, route: LatLng[], futureRoute: LatLng[]) {
    // Check for trams ahead
    for (let i = 1; i < futureRoute.length; i++) {
      for (const item of this.tramsOnMap) {
        if (
          item != tram &&
          this.laysOnSegment(futureRoute[i - 1], futureRoute[i], item.marker.getLatLng())
        ) return false
      }
    }

    // Check intersecting paths
    for (const node of futureRoute) {
      if ((this.occupiedNodes.get(this.latLngKey(node)) ?? tram) != tram) return false
    }

    for (const node of this.previousRoutes.get(tram) ?? []) {
      this.occupiedNodes.delete(this.latLngKey(node))
    }

    for (const node of route) {
      this.occupiedNodes.set(this.latLngKey(node), tram)
    }

    this.previousRoutes.set(tram, route)

    // Check for trams waiting for registration
    for (const item of this.tramsWaitingForRegistration) {
      if (!this.occupiedNodes.has(this.latLngKey(item.marker.getLatLng()))) {
        this.addTramToMap(item)
        this.tramsWaitingForRegistration.delete(item)
      }
    }

    return true
  }
}
