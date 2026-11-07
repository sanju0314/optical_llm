def validate_design(design: dict):
    # Top-level required fields
    required_top_keys = [
        "device_type",
        "lambda0_nm",
        "wavelength_range_nm",
        "materials",
        "structure",
        "optical_conditions",
        "optimization",
        "targets"
    ]

    for key in required_top_keys:
        if key not in design:
            raise ValueError(f"Missing top-level key: {key}")

    # device_type
    if design["device_type"] != "bragg_stack":
        raise ValueError("device_type must be 'bragg_stack'")

    # lambda0_nm
    if not isinstance(design["lambda0_nm"], (int, float)):
        raise ValueError("lambda0_nm must be a number")
    if design["lambda0_nm"] <= 0:
        raise ValueError("lambda0_nm must be > 0")

    # wavelength_range_nm
    wr = design["wavelength_range_nm"]
    if not isinstance(wr, list) or len(wr) != 2:
        raise ValueError("wavelength_range_nm must be a list of 2 values")
    if wr[0] >= wr[1]:
        raise ValueError("wavelength_range_nm must be [min, max] with min < max")

    # materials
    materials = design["materials"]
    if not isinstance(materials, list) or len(materials) != 2:
        raise ValueError("materials must contain exactly 2 materials")

    for i, mat in enumerate(materials, start=1):
        if "name" not in mat:
            raise ValueError(f"Material {i} missing 'name'")
        if "n" not in mat:
            raise ValueError(f"Material {i} missing 'n'")
        if not isinstance(mat["n"], (int, float)):
            raise ValueError(f"Material {i} refractive index n must be numeric")
        if mat["n"] <= 0:
            raise ValueError(f"Material {i} refractive index n must be > 0")

    # structure
    structure = design["structure"]
    required_structure_keys = ["periods", "d1_nm", "d2_nm", "order"]
    for key in required_structure_keys:
        if key not in structure:
            raise ValueError(f"structure missing key: {key}")

    if int(structure["periods"]) <= 0:
        raise ValueError("structure.periods must be > 0")

    if structure["d1_nm"] <= 0:
        raise ValueError("structure.d1_nm must be > 0")

    if structure["d2_nm"] <= 0:
        raise ValueError("structure.d2_nm must be > 0")

    if structure["order"] not in ["HL", "LH"]:
        raise ValueError("structure.order must be 'HL' or 'LH'")

    # optical_conditions
    optical = design["optical_conditions"]
    required_optical_keys = ["incident_angle_deg", "polarization"]
    for key in required_optical_keys:
        if key not in optical:
            raise ValueError(f"optical_conditions missing key: {key}")

    if optical["polarization"] not in ["TE", "TM"]:
        raise ValueError("optical_conditions.polarization must be 'TE' or 'TM'")

    # optimization
    optimization = design["optimization"]
    required_opt_keys = ["method", "trials"]
    for key in required_opt_keys:
        if key not in optimization:
            raise ValueError(f"optimization missing key: {key}")

    if optimization["method"] != "bayesian":
        raise ValueError("optimization.method must be 'bayesian'")

    if int(optimization["trials"]) <= 0:
        raise ValueError("optimization.trials must be > 0")

    # targets
    targets = design["targets"]
    required_target_keys = [
        "max_center_error_nm",
        "min_bandgap_width_nm",
        "max_minT"
    ]
    for key in required_target_keys:
        if key not in targets:
            raise ValueError(f"targets missing key: {key}")

    if targets["max_center_error_nm"] <= 0:
        raise ValueError("targets.max_center_error_nm must be > 0")

    if targets["min_bandgap_width_nm"] <= 0:
        raise ValueError("targets.min_bandgap_width_nm must be > 0")

    if targets["max_minT"] < 0:
        raise ValueError("targets.max_minT must be >= 0")

    return True