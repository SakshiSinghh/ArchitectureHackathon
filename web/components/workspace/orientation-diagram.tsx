"use client"

/**
 * Top-down SVG diagram showing:
 * - Compass rose (fixed N/E/S/W)
 * - Sun arc from E to W (fixed)
 * - Building footprint rectangle rotated by orientation_deg
 * - Facade colours based on solar exposure (west=orange, south=yellow, north=blue, east=peach)
 */

type Props = {
  orientationDeg: number
  size?: number
}

// Facade heat colours by compass direction the face points toward
const FACADE_FILL: Record<string, string> = {
  north: "#bfdbfe",   // blue-200 — cool
  east: "#fed7aa",    // orange-200 — morning sun
  south: "#fef08a",   // yellow-200 — midday
  west: "#fb923c",    // orange-400 — hot afternoon
}

function facadeDirection(wallAngleDeg: number): string {
  const norm = ((wallAngleDeg % 360) + 360) % 360
  if (norm >= 337.5 || norm < 22.5) return "north"
  if (norm < 67.5) return "north-east"
  if (norm < 112.5) return "east"
  if (norm < 157.5) return "south-east"
  if (norm < 202.5) return "south"
  if (norm < 247.5) return "south-west"
  if (norm < 292.5) return "west"
  return "north-west"
}

function facadeColor(dir: string): string {
  if (dir.includes("west")) return FACADE_FILL.west
  if (dir.includes("south")) return FACADE_FILL.south
  if (dir.includes("east")) return FACADE_FILL.east
  return FACADE_FILL.north
}

export function OrientationDiagram({ orientationDeg, size = 140 }: Props) {
  const cx = size / 2
  const cy = size / 2
  const r = size * 0.38          // compass circle radius
  const bw = size * 0.28         // building width
  const bh = size * 0.42         // building height
  const sunR = r * 1.05          // sun arc radius

  // Building rectangle corners (unrotated, centred at origin)
  const hw = bw / 2
  const hh = bh / 2

  // The four facade directions when building is rotated by orientationDeg
  // orientationDeg = 0 means primary facade faces North (top)
  const topDir = facadeDirection(orientationDeg)           // top face
  const rightDir = facadeDirection(orientationDeg + 90)    // right face
  const bottomDir = facadeDirection(orientationDeg + 180)  // bottom face
  const leftDir = facadeDirection(orientationDeg + 270)    // left face

  // Sun arc: rises in east (90deg), sets in west (270deg), peaks at south (180deg) for northern hemisphere
  // Parametric: angle in SVG coords (0=right=east, going clockwise)
  const sunArcPath = (() => {
    // E is at angle 0 in standard math, but SVG y is flipped
    // In our compass: E = right = (cx+r, cy), W = left = (cx-r, cy)
    // Arc goes E -> S -> W (lower half in SVG = southern sky for northern hemisphere)
    const ex = cx + sunR
    const ey = cy
    const wx = cx - sunR
    const wy = cy
    return `M ${ex} ${ey} A ${sunR} ${sunR * 0.5} 0 0 1 ${wx} ${wy}`
  })()

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className="overflow-visible"
      aria-label={`Building orientation ${orientationDeg} degrees`}
    >
      {/* Compass ring */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e8f0" strokeWidth="1" />

      {/* Compass tick marks */}
      {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
        const rad = (deg - 90) * (Math.PI / 180)
        const inner = r * 0.88
        const outer = r
        return (
          <line
            key={deg}
            x1={cx + inner * Math.cos(rad)}
            y1={cy + inner * Math.sin(rad)}
            x2={cx + outer * Math.cos(rad)}
            y2={cy + outer * Math.sin(rad)}
            stroke="#cbd5e1"
            strokeWidth={deg % 90 === 0 ? 1.5 : 0.8}
          />
        )
      })}

      {/* Cardinal labels */}
      {[
        { label: "N", deg: 0 },
        { label: "E", deg: 90 },
        { label: "S", deg: 180 },
        { label: "W", deg: 270 },
      ].map(({ label, deg }) => {
        const rad = (deg - 90) * (Math.PI / 180)
        const dist = r * 1.18
        return (
          <text
            key={label}
            x={cx + dist * Math.cos(rad)}
            y={cy + dist * Math.sin(rad)}
            textAnchor="middle"
            dominantBaseline="central"
            fontSize={size * 0.09}
            fontWeight="600"
            fill={label === "N" ? "#1e40af" : "#64748b"}
          >
            {label}
          </text>
        )
      })}

      {/* Sun arc (E to W through south) */}
      <path
        d={sunArcPath}
        fill="none"
        stroke="#f59e0b"
        strokeWidth="1.5"
        strokeDasharray="3 2"
        opacity="0.7"
      />
      {/* Sun icon at midpoint (south) */}
      <circle cx={cx} cy={cy + sunR * 0.5} r={size * 0.03} fill="#f59e0b" opacity="0.8" />

      {/* Building footprint — rotated group */}
      <g transform={`rotate(${orientationDeg}, ${cx}, ${cy})`}>
        {/* Bottom face */}
        <rect
          x={cx - hw}
          y={cy + hh - size * 0.025}
          width={bw}
          height={size * 0.025}
          fill={facadeColor(bottomDir)}
          rx="1"
        />
        {/* Top face */}
        <rect
          x={cx - hw}
          y={cy - hh}
          width={bw}
          height={size * 0.025}
          fill={facadeColor(topDir)}
          rx="1"
        />
        {/* Left face */}
        <rect
          x={cx - hw - size * 0.025}
          y={cy - hh}
          width={size * 0.025}
          height={bh}
          fill={facadeColor(leftDir)}
          rx="1"
        />
        {/* Right face */}
        <rect
          x={cx + hw}
          y={cy - hh}
          width={size * 0.025}
          height={bh}
          fill={facadeColor(rightDir)}
          rx="1"
        />
        {/* Building body */}
        <rect
          x={cx - hw}
          y={cy - hh}
          width={bw}
          height={bh}
          fill="white"
          stroke="#94a3b8"
          strokeWidth="1.2"
          rx="2"
        />
        {/* North arrow on building (shows primary facade direction) */}
        <polygon
          points={`${cx},${cy - hh + size * 0.04} ${cx - size * 0.025},${cy - hh + size * 0.1} ${cx + size * 0.025},${cy - hh + size * 0.1}`}
          fill="#1e40af"
          opacity="0.6"
        />
      </g>
    </svg>
  )
}
