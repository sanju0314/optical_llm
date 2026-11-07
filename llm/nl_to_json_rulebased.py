import re
import copy
from llm.default_design import DEFAULT_DESIGN

# Main material database
MATERIAL_DB = {
    "SiO2": 1.45,
    "TiO2": 2.4,
    "Al2O3": 1.76,
    "MgF2": 1.38,
    "ZnS": 2.35,
    "Si": 3.48,
    "AlAs": 2.9,
    "GaAs": 3.3
}

# Aliases / alternate spellings
MATERIAL_ALIASES = {
    "sio2": "SiO2",
    "silicon dioxide": "SiO2",
    "tio2": "TiO2",
    "titanium dioxide": "TiO2",
    "al2o3": "Al2O3",
    "aluminum oxide": "Al2O3",
    "aluminium oxide": "Al2O3",
    "mgf2": "MgF2",
    "magnesium fluoride": "MgF2",
    "zns": "ZnS",
    "zinc sulfide": "ZnS",
    "zinc sulphide": "ZnS",
    "si": "Si",
    "silicon": "Si",
    "alas": "AlAs",
    "aluminium arsenide": "AlAs",
    "gaas": "GaAs",
    "gallium arsenide": "GaAs"
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_lambda_nm(text: str):
    text_low = normalize_text(text)

    nm_match = re.search(r'(\d+(?:\.\d+)?)\s*nm', text_low)
    if nm_match:
        return float(nm_match.group(1))

    um_match = re.search(r'(\d+(?:\.\d+)?)\s*(um|micron|microns)', text_low)
    if um_match:
        return float(um_match.group(1)) * 1000.0

    return None


def extract_wavelength_range(text: str):
    text_low = normalize_text(text)

    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*nm',
        r'range\s*(\d+(?:\.\d+)?)\s*nm\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*nm',
        r'from\s*(\d+(?:\.\d+)?)\s*nm\s*to\s*(\d+(?:\.\d+)?)\s*nm'
    ]

    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            low = float(match.group(1))
            high = float(match.group(2))
            if low < high:
                return [low, high]

    return None


def extract_materials(text: str):
    text_low = normalize_text(text)
    found = []

    for alias, canonical_name in MATERIAL_ALIASES.items():
        if alias in text_low and canonical_name not in found:
            found.append(canonical_name)

    return found[:2]


def build_material_objects(material_names):
    materials = []
    for name in material_names:
        materials.append({
            "name": name,
            "n": MATERIAL_DB[name]
        })
    return materials


def extract_periods(text: str):
    text_low = normalize_text(text)
    match = re.search(r'(\d+)\s*(periods|pairs)', text_low)
    if match:
        return int(match.group(1))
    return None


def extract_order(text: str):
    text_up = text.upper()
    if "LH" in text_up:
        return "LH"
    if "HL" in text_up:
        return "HL"
    return None


def extract_polarization(text: str):
    text_up = text.upper()
    if "TM" in text_up:
        return "TM"
    if "TE" in text_up:
        return "TE"
    return None


def extract_incident_angle(text: str):
    text_low = normalize_text(text)
    match = re.search(r'(\d+(?:\.\d+)?)\s*(deg|degree|degrees)', text_low)
    if match:
        return float(match.group(1))
    return None


def extract_trials(text: str):
    text_low = normalize_text(text)
    match = re.search(r'(\d+)\s*trials', text_low)
    if match:
        return int(match.group(1))
    return None


def extract_max_center_error(text: str):
    text_low = normalize_text(text)
    patterns = [
        r'center error\s*(?:of|=|below|less than|under|at most)?\s*(\d+(?:\.\d+)?)\s*nm',
        r'max center error\s*(?:of|=)?\s*(\d+(?:\.\d+)?)\s*nm'
    ]
    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            return float(match.group(1))
    return None


def extract_min_bandgap_width(text: str):
    text_low = normalize_text(text)
    patterns = [
        r'bandgap width\s*(?:of|=|at least|above|greater than|more than)?\s*(\d+(?:\.\d+)?)\s*nm',
        r'min bandgap width\s*(?:of|=)?\s*(\d+(?:\.\d+)?)\s*nm'
    ]
    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            return float(match.group(1))
    return None


def extract_max_minT(text: str):
    text_low = normalize_text(text)
    patterns = [
        r'(?:mint|max mint|min t|minimum transmission)\s*(?:of|=|below|less than|under|at most)?\s*(0?\.\d+|\d+)',
        r'max minimum transmission\s*(?:of|=)?\s*(0?\.\d+|\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            return float(match.group(1))
    return None


def parse_text_to_design(text: str):
    design = copy.deepcopy(DEFAULT_DESIGN)

    lambda_nm = extract_lambda_nm(text)
    if lambda_nm is not None:
        design["lambda0_nm"] = lambda_nm

    wavelength_range = extract_wavelength_range(text)
    if wavelength_range is not None:
        design["wavelength_range_nm"] = wavelength_range

    materials = extract_materials(text)
    if len(materials) == 2:
        design["materials"] = build_material_objects(materials)

    periods = extract_periods(text)
    if periods is not None:
        design["structure"]["periods"] = periods

    order = extract_order(text)
    if order is not None:
        design["structure"]["order"] = order

    polarization = extract_polarization(text)
    if polarization is not None:
        design["optical_conditions"]["polarization"] = polarization

    angle = extract_incident_angle(text)
    if angle is not None:
        design["optical_conditions"]["incident_angle_deg"] = angle

    trials = extract_trials(text)
    if trials is not None:
        design["optimization"]["trials"] = trials

    max_center_error = extract_max_center_error(text)
    if max_center_error is not None:
        design["targets"]["max_center_error_nm"] = max_center_error

    min_bandgap_width = extract_min_bandgap_width(text)
    if min_bandgap_width is not None:
        design["targets"]["min_bandgap_width_nm"] = min_bandgap_width

    max_minT = extract_max_minT(text)
    if max_minT is not None:
        design["targets"]["max_minT"] = max_minT

    return design