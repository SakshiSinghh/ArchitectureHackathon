# ArchEnv GHPython Component - Level 1 (Hackathon MVP)
# ---------------------------------------------------------
# Inputs:  orientation_deg (float), location (str),
#          building_type (str), run (bool)
# Outputs: energy_risk, daylight_potential, ventilation_potential,
#          best_orientation, best_score, narrative, all_options

import json

try:
    import urllib2 as _urllib
    def _post(url, data):
        req = _urllib.Request(url, json.dumps(data), {"Content-Type": "application/json"})
        return json.loads(_urllib.urlopen(req, timeout=10).read())
except ImportError:
    import urllib.request as _urllib
    def _post(url, data):
        body = json.dumps(data).encode("utf-8")
        req = _urllib.Request(url, body, {"Content-Type": "application/json"})
        with _urllib.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))

_deg   = float(orientation_deg) if orientation_deg is not None else 0.0
_loc   = str(location)          if location         else "Pune"
_btype = str(building_type)     if building_type    else "office"

energy_risk = daylight_potential = ventilation_potential = None
best_orientation = narrative = all_options = None
best_score = None

if not run:
    all_options = "Toggle run = True to call the backend."
else:
    payload = {
        "project_state": {
            "project_name": "Grasshopper",
            "input_mode":   "manual_form",
            "brief_text":   None,
            "site": {
                "location_name": _loc,
                "latitude":      18.52,
                "longitude":     73.85,
                "climate_notes": None,
            },
            "building": {
                "building_type":        _btype,
                "width_m":              20,
                "depth_m":              28,
                "height_m":             12,
                "floors":               3,
                "orientation_deg":      _deg,
                "window_to_wall_ratio": 0.35,
                "geometry_notes":       None,
            },
            "constraints": {
                "hard_constraints": [],
                "soft_constraints": [],
            },
            "priorities": {
                "energy":         0.3,
                "daylight":       0.25,
                "ventilation":    0.2,
                "cost":           0.1,
                "aesthetics":     0.05,
                "sustainability": 0.1,
            },
            "floor_plan_analysis": None,
            "baseline_results": {
                "energy_risk":           None,
                "daylight_potential":    None,
                "ventilation_potential": None,
                "heat_exposure":         None,
                "solar_exposure":        None,
                "ventilation_context":   None,
                "narrative_insight":     None,
                "mitigation_options":    [],
            },
        }
    }

    try:
        result = _post("http://localhost:8000/api/v1/analysis/orientation-options", payload)
        options = result.get("options", [])

        top = next((o for o in options if o["rank"] == 1), options[0] if options else None)
        if top:
            best_orientation = top["label"]
            best_score       = round(top["composite_score"], 4)
            narrative        = top["narrative"]

        current = next((o for o in options if o.get("is_current")), top)
        if current:
            energy_risk           = round(current["energy_risk"],           3)
            daylight_potential    = round(current["daylight_potential"],    3)
            ventilation_potential = round(current["ventilation_potential"], 3)

        lines = ["=== Orientation Options for " + _loc + " ==="]
        for o in sorted(options, key=lambda x: x["rank"]):
            tag = "  [YOUR CURRENT]" if o.get("is_current") else ""
            lines.append(
                "#{rank}  {label}{tag}  score={composite_score:.4f}"
                "   energy={energy_risk:.2f}  daylight={daylight_potential:.2f}  vent={ventilation_potential:.2f}".format(
                    tag=tag, **o
                )
            )
            lines.append("     " + o["narrative"])
        all_options = "
".join(lines)

    except Exception as ex:
        all_options = "ERROR: " + str(ex)
        energy_risk = daylight_potential = ventilation_potential = 0.0
        best_orientation = "error"
        best_score = 0.0
        narrative = str(ex)
