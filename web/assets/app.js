const elements = {
  status: document.querySelector('#status-pill'),
  refresh: document.querySelector('#refresh-button'),
  temperature: document.querySelector('#temperature'),
  interval: document.querySelector('#interval'),
  target: document.querySelector('#target-id'),
  generated: document.querySelector('#generated-at'),
  spread: document.querySelector('#network-spread'),
  effectiveSample: document.querySelector('#effective-sample'),
  stationCount: document.querySelector('#station-count'),
  configuredCount: document.querySelector('#configured-count'),
  wind: document.querySelector('#wind-context'),
  map: document.querySelector('#station-map'),
  distribution: document.querySelector('#distribution'),
  stationTable: document.querySelector('#station-table'),
}

function number(value, digits = 2) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed.toFixed(digits) : '--'
}

function clock(value) {
  if (!value) return 'Not generated'
  const date = new Date(value)
  return Number.isNaN(date.valueOf()) ? String(value) : date.toLocaleString()
}

function renderMap(stations) {
  elements.map.replaceChildren()
  const maximumDistance = Math.max(...stations.map((station) => Number(station.distance_miles)), 1)
  const maximumWeight = Math.max(...stations.map((station) => Number(station.weight)), 0.01)
  stations.forEach((station) => {
    const angle = ((Number(station.bearing_degrees) - 90) * Math.PI) / 180
    const radius = 12 + (Number(station.distance_miles) / maximumDistance) * 35
    const x = 50 + Math.cos(angle) * radius
    const y = 50 + Math.sin(angle) * radius
    const weightRatio = Number(station.weight) / maximumWeight
    const dot = document.createElement('button')
    dot.type = 'button'
    dot.className = 'station-dot'
    dot.style.left = `${x}%`
    dot.style.top = `${y}%`
    dot.style.width = `${12 + weightRatio * 18}px`
    dot.style.height = `${12 + weightRatio * 18}px`
    dot.style.opacity = String(0.45 + weightRatio * 0.55)
    dot.title = `${station.station_id}: ${number(station.corrected_temperature_f, 1)}°F · weight ${number(Number(station.weight) * 100, 1)}%`
    dot.setAttribute('aria-label', dot.title)
    elements.map.append(dot)
  })
}

function renderDistribution(rows) {
  elements.distribution.replaceChildren()
  if (!rows.length) {
    elements.distribution.textContent = 'No threshold distribution available.'
    return
  }
  const maximum = Math.max(...rows.map((row) => Number(row.probability)), 0.01)
  rows.forEach((row) => {
    const item = document.createElement('div')
    item.className = 'distribution-row'
    const label = document.createElement('span')
    label.textContent = `${number(row.lower_f, 0)}–${number(row.upper_f, 0)}°F`
    const track = document.createElement('div')
    track.className = 'distribution-track'
    const bar = document.createElement('div')
    bar.className = 'distribution-bar'
    bar.style.width = `${(Number(row.probability) / maximum) * 100}%`
    track.append(bar)
    const probability = document.createElement('strong')
    probability.textContent = `${number(Number(row.probability) * 100, 1)}%`
    item.append(label, track, probability)
    elements.distribution.append(item)
  })
}

function renderTable(stations) {
  elements.stationTable.replaceChildren()
  stations.forEach((station) => {
    const row = document.createElement('tr')
    const values = [
      station.station_id,
      `${number(station.temperature_f, 1)}°F`,
      `${number(station.corrected_temperature_f, 1)}°F`,
      `${number(station.distance_miles, 2)} mi`,
      `${number(Number(station.age_seconds) / 60, 1)} min`,
      String(station.sector),
      `${number(Number(station.weight) * 100, 1)}%`,
    ]
    values.forEach((value, index) => {
      const cell = document.createElement(index === 0 ? 'th' : 'td')
      cell.textContent = value
      row.append(cell)
    })
    elements.stationTable.append(row)
  })
}

function render(payload) {
  const estimate = payload.estimate || {}
  const stations = payload.station_contributions || []
  const target = payload.target || {}
  const wind = payload.wind_context || {}
  elements.status.textContent = String(payload.status || 'Unknown').replaceAll('_', ' ')
  elements.status.dataset.status = payload.status || 'unknown'
  elements.temperature.textContent = number(estimate.temperature_f, 2)
  const interval = estimate.interval_95_f || []
  elements.interval.textContent = interval.length === 2
    ? `95% interval ${number(interval[0], 2)}–${number(interval[1], 2)}°F · σ ${number(estimate.sigma_f, 2)}°F`
    : '95% interval unavailable'
  elements.target.textContent = target.target_id || 'Target unavailable'
  elements.generated.textContent = clock(payload.generated_at)
  elements.spread.textContent = `${number(estimate.network_spread_f, 2)}°F`
  elements.effectiveSample.textContent = number(estimate.effective_sample_size, 2)
  elements.stationCount.textContent = String(estimate.usable_station_count ?? '--')
  elements.configuredCount.textContent = `${estimate.configured_station_count ?? '--'} configured stations`
  elements.wind.textContent = wind.direction_from_deg == null
    ? 'No wind context'
    : `Wind from ${number(wind.direction_from_deg, 0)}° at ${number(wind.speed_mph, 1)} mph`
  renderMap(stations)
  renderDistribution(estimate.threshold_distribution || [])
  renderTable(stations)
}

async function load() {
  elements.refresh.disabled = true
  elements.status.textContent = 'Loading'
  try {
    const response = await fetch('/api/estimate', { headers: { Accept: 'application/json' } })
    if (!response.ok) throw new Error(`API returned ${response.status}`)
    render(await response.json())
  } catch (error) {
    elements.status.textContent = 'Unavailable'
    elements.interval.textContent = error instanceof Error ? error.message : String(error)
  } finally {
    elements.refresh.disabled = false
  }
}

elements.refresh.addEventListener('click', load)
load()
