export interface GlobalSettings {
  day_types: string[],
  stop_locations: Array<{
    id: number,
    name: string,
    latitude: number,
    longitude: number
  }>,
  tram_routes: Record<number, Record<number, Array<{
    latitude: number,
    longitude: number,
    distance: number
  }>>>
}

export interface TramPassages {
  passage_id: number,
  tram_line: string,
  stops: {
    node_id: number,
    name: string,
    latitude: number,
    longitude: number,
    hour: number,
    minute: number
  }[]
}
