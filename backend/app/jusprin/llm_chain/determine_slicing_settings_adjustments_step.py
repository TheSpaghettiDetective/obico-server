import instructor
import os
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Literal
import sentry_sdk
import copy
import json
from textwrap import dedent
from .utils import combined_params, parse_json_string_fields

class Percentage(str):
    """Custom Pydantic type that only allows percentage strings (e.g., '50%')."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, field_info=None):
        if isinstance(value, str):
            value = value.strip()  # Remove leading/trailing whitespace

            if value.endswith('%'):  # Ensure it ends with a '%'
                try:
                    float(value.rstrip('%'))  # Check if it can be converted to a float
                    return cls(value)  # Store the original value unchanged
                except ValueError:
                    raise ValueError(f"Invalid percentage format: {value}")

        raise ValueError(f"Value must be a percentage string (e.g., '50%'), got {value}")

class FilamentParamOverride(BaseModel):
    cool_plate_temp: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    eng_plate_temp: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    hot_plate_temp: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    textured_plate_temp: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    cool_plate_temp_initial_layer: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    eng_plate_temp_initial_layer: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    hot_plate_temp_initial_layer: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    textured_plate_temp_initial_layer: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    overhang_fan_threshold: Optional[List[Literal['0%', '10%', '25%', '50%', '75%', '95%']]] = Field(default=None, min_length=1, max_length=1)
    overhang_fan_speed: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    slow_down_for_layer_cooling: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    close_fan_the_first_x_layers: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    filament_end_gcode: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    filament_flow_ratio: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    reduce_fan_stop_start_freq: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    fan_cooling_layer_time: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_cost: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_density: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_diameter: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_max_volumetric_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_minimal_purge_on_wipe_tower: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_settings_id: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    filament_soluble: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    filament_type: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    filament_vendor: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    nozzle_temperature_initial_layer: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    full_fan_speed_layer: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    fan_max_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    fan_min_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    slow_down_min_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    slow_down_layer_time: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_start_gcode: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    nozzle_temperature: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    temperature_vitrification: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    nozzle_temperature_range_low: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    nozzle_temperature_range_high: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    additional_cooling_fan_speed: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    required_nozzle_HRC: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    filament_is_support: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    enable_pressure_advance: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    pressure_advance: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_cooling_moves: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    filament_cooling_initial_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_cooling_final_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    enable_overhang_bridge_fan: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    support_material_interface_fan_speed: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    activate_air_filtration: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    complete_print_exhaust_fan_speed: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    during_print_exhaust_fan_speed: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    dont_slow_down_outer_wall: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    activate_chamber_temp_control: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    chamber_temperature: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    filament_loading_speed_start: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_loading_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_unloading_speed_start: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_unloading_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    compatible_prints: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    default_filament_colour: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    filament_multitool_ramming: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    filament_multitool_ramming_flow: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_multitool_ramming_volume: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_notes: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    filament_ramming_parameters: Optional[List[str]] = Field(default=None, min_length=1, max_length=1)
    filament_shrink: Optional[str] = None
    filament_toolchange_delay: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    pellet_flow_coefficient: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_stamping_distance: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_stamping_loading_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    idle_temperature: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    filament_deretraction_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retraction_minimum_travel: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_before_wipe: Optional[str] = None
    filament_retract_when_changing_layer: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    filament_retraction_length: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_z_hop: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_z_hop_types: Optional[List[Literal['Auto Lift', 'Normal Lift', 'Slope Lift', 'Spiral Lift']]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_restart_extra: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retraction_speed: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_wipe: Optional[List[bool]] = Field(default=None, min_length=1, max_length=1)
    filament_wipe_distance: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    chamber_temperatures: Optional[List[int]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_lift_above: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_lift_below: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_lift_enforce: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_lift_above_enforce: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)
    filament_retract_lift_below_enforce: Optional[List[float]] = Field(default=None, min_length=1, max_length=1)

class PrintProcessParamOverride(BaseModel):
    adaptive_layer_height: Optional[bool] = None
    reduce_crossing_wall: Optional[bool] = None
    bridge_flow: Optional[float] = None
    bridge_speed: Optional[float] = None
    brim_width: Optional[float] = None
    print_sequence: Optional[Literal['by layer', 'by object']] = None
    default_acceleration: Optional[float] = None
    bridge_no_support: Optional[bool] = None
    elefant_foot_compensation: Optional[float] = None
    outer_wall_line_width: Optional[Union[float, Percentage]] = None
    outer_wall_speed: Optional[float] = None
    line_width: Optional[Union[float, Percentage]] = None
    infill_direction: Optional[float] = None
    sparse_infill_density: Optional[float] = None
    sparse_infill_pattern: Optional[Literal['concentric', 'zig-zag', 'grid', 'line', 'cubic', 'triangles', 'tri-hexagon', 'gyroid', 'honeycomb', 'adaptivecubic', 'alignedrectilinear', '3dhoneycomb', 'hilbertcurve', 'archimedeanchords', 'octagramspiral', 'supportcubic', 'lightning', 'crosshatch']] = None
    initial_layer_line_width: Optional[Union[float, Percentage]] = None
    initial_layer_print_height: Optional[float] = None
    initial_layer_speed: Optional[float] = None
    gap_infill_speed: Optional[float] = None
    infill_combination: Optional[bool] = None
    sparse_infill_line_width: Optional[Union[float, Percentage]] = None
    infill_wall_overlap: Optional[float] = None
    sparse_infill_speed: Optional[float] = None
    interface_shells: Optional[bool] = None
    detect_overhang_wall: Optional[bool] = None
    reduce_infill_retraction: Optional[bool] = None
    filename_format: Optional[str] = None
    wall_loops: Optional[int] = None
    inner_wall_line_width: Optional[Union[float, Percentage]] = None
    inner_wall_speed: Optional[float] = None
    print_settings_id: Optional[str] = None
    raft_layers: Optional[int] = None
    seam_position: Optional[Literal['nearest', 'aligned', 'back', 'random']] = None
    skirt_distance: Optional[float] = None
    skirt_height: Optional[int] = None
    minimum_sparse_infill_area: Optional[float] = None
    internal_solid_infill_line_width: Optional[Union[float, Percentage]] = None
    internal_solid_infill_speed: Optional[float] = None
    spiral_mode: Optional[bool] = None
    standby_temperature_delta: Optional[int] = None
    enable_support: Optional[bool] = None
    support_filament: Optional[int] = None
    support_line_width: Optional[Union[float, Percentage]] = None
    support_interface_filament: Optional[int] = None
    support_on_build_plate_only: Optional[bool] = None
    support_top_z_distance: Optional[float] = None
    support_interface_loop_pattern: Optional[bool] = None
    support_interface_top_layers: Optional[int] = None
    support_interface_spacing: Optional[float] = None
    support_interface_speed: Optional[float] = None
    support_base_pattern: Optional[Literal['default', 'rectilinear', 'rectilinear-grid', 'honeycomb', 'lightning', 'hollow']] = None
    support_base_pattern_spacing: Optional[float] = None
    support_speed: Optional[float] = None
    support_threshold_angle: Optional[int] = None
    support_object_xy_distance: Optional[float] = None
    detect_thin_wall: Optional[bool] = None
    top_surface_line_width: Optional[Union[float, Percentage]] = None
    top_surface_speed: Optional[float] = None
    travel_speed: Optional[float] = None
    enable_prime_tower: Optional[bool] = None
    prime_tower_width: Optional[float] = None
    xy_hole_compensation: Optional[float] = None
    xy_contour_compensation: Optional[float] = None
    max_travel_detour_distance: Optional[Union[float, Percentage]] = None
    bottom_surface_pattern: Optional[Literal['concentric', 'zig-zag', 'grid', 'line', 'cubic', 'triangles', 'tri-hexagon', 'gyroid', 'honeycomb', 'adaptivecubic', 'alignedrectilinear', '3dhoneycomb', 'hilbertcurve', 'archimedeanchords', 'octagramspiral', 'supportcubic', 'lightning', 'crosshatch']] = None
    bottom_shell_layers: Optional[int] = None
    bottom_shell_thickness: Optional[float] = None
    brim_object_gap: Optional[float] = None
    top_surface_acceleration: Optional[float] = None
    draft_shield: Optional[Literal['disabled', 'enabled']] = None
    enable_arc_fitting: Optional[bool] = None
    initial_layer_acceleration: Optional[float] = None
    travel_acceleration: Optional[float] = None
    inner_wall_acceleration: Optional[float] = None
    ironing_flow: Optional[float] = None
    ironing_spacing: Optional[float] = None
    ironing_speed: Optional[float] = None
    ironing_type: Optional[Literal['no ironing', 'top', 'topmost', 'solid']] = None
    layer_height: Optional[float] = None
    overhang_1_4_speed: Optional[Union[float, Percentage]] = None
    overhang_2_4_speed: Optional[Union[float, Percentage]] = None
    overhang_3_4_speed: Optional[Union[float, Percentage]] = None
    overhang_4_4_speed: Optional[Union[float, Percentage]] = None
    skirt_loops: Optional[int] = None
    resolution: Optional[float] = None
    support_type: Optional[Literal['normal(auto)', 'tree(auto)', 'normal(manual)', 'tree(manual)']] = None
    support_style: Optional[Literal['default', 'grid', 'snug', 'organic', 'tree_slim', 'tree_strong', 'tree_hybrid']] = None
    support_interface_bottom_layers: Optional[int] = None
    tree_support_branch_angle: Optional[float] = None
    tree_support_wall_count: Optional[int] = None
    top_surface_pattern: Optional[Literal['concentric', 'zig-zag', 'monotonic', 'monotonicline', 'alignedrectilinear', 'hilbertcurve', 'archimedeanchords', 'octagramspiral']] = None
    top_shell_layers: Optional[int] = None
    top_shell_thickness: Optional[float] = None
    initial_layer_infill_speed: Optional[float] = None
    wipe_tower_no_sparse_layers: Optional[bool] = None
    initial_layer_travel_speed: Optional[Union[float, Percentage]] = None
    outer_wall_acceleration: Optional[float] = None
    exclude_object: Optional[bool] = None
    internal_bridge_speed: Optional[Union[float, Percentage]] = None
    infill_anchor: Optional[Union[float, Percentage]] = None
    infill_anchor_max: Optional[Union[float, Percentage]] = None
    support_bottom_z_distance: Optional[float] = None
    small_perimeter_speed: Optional[Union[float, Percentage]] = None
    internal_solid_infill_acceleration: Optional[Union[float, Percentage]] = None
    sparse_infill_acceleration: Optional[Union[float, Percentage]] = None
    bridge_acceleration: Optional[Union[float, Percentage]] = None
    enable_overhang_speed: Optional[bool] = None
    precise_outer_wall: Optional[bool] = None
    ensure_vertical_shell_thickness: Optional[Literal['none', 'ensure_critical_only', 'ensure_moderate', 'ensure_all']] = None
    default_jerk: Optional[float] = None
    outer_wall_jerk: Optional[float] = None
    inner_wall_jerk: Optional[float] = None
    infill_jerk: Optional[float] = None
    top_surface_jerk: Optional[float] = None
    initial_layer_jerk: Optional[float] = None
    travel_jerk: Optional[float] = None
    independent_support_layer_height: Optional[bool] = None
    support_interface_pattern: Optional[Literal['auto', 'rectilinear', 'concentric', 'rectilinear_interlaced', 'grid']] = None
    small_perimeter_threshold: Optional[float] = None
    accel_to_decel_enable: Optional[bool] = None
    accel_to_decel_factor: Optional[float] = None
    tree_support_with_infill: Optional[bool] = None
    only_one_wall_top: Optional[bool] = None
    skirt_speed: Optional[float] = None
    wall_generator: Optional[Literal['classic', 'arachne']] = None
    seam_gap: Optional[Union[float, Percentage]] = None
    support_expansion: Optional[float] = None
    tree_support_branch_diameter: Optional[float] = None
    gcode_label_objects: Optional[bool] = None
    internal_solid_infill_pattern: Optional[Literal['concentric', 'zig-zag', 'grid', 'line', 'cubic', 'triangles', 'tri-hexagon', 'gyroid', 'honeycomb', 'adaptivecubic', 'alignedrectilinear', '3dhoneycomb', 'hilbertcurve', 'archimedeanchords', 'octagramspiral', 'supportcubic', 'lightning', 'crosshatch']] = None
    filter_out_gap_fill: Optional[float] = None
    notes: Optional[str] = None
    brim_type: Optional[Literal['auto_brim', 'brim_ears', 'outer_only', 'inner_only', 'outer_and_inner', 'no_brim']] = None
    seam_slope_conditional: Optional[bool] = None
    seam_slope_inner_walls: Optional[bool] = None
    seam_slope_entire_loop: Optional[bool] = None
    role_based_wipe_speed: Optional[bool] = None
    wipe_speed: Optional[Union[float, Percentage]] = None
    extra_perimeters_on_overhangs: Optional[bool] = None
    slow_down_layers: Optional[int] = None
    wall_sequence: Optional[Literal['inner wall/outer wall', 'outer wall/inner wall', 'inner-outer-inner wall']] = None
    slowdown_for_curled_perimeters: Optional[bool] = None
    min_skirt_length: Optional[float] = None
    raft_first_layer_density: Optional[float] = None
    raft_first_layer_expansion: Optional[float] = None
    wall_distribution_count: Optional[int] = None
    bridge_angle: Optional[float] = None
    enforce_support_layers: Optional[int] = None
    min_bead_width: Optional[float] = None
    min_feature_size: Optional[float] = None
    ooze_prevention: Optional[bool] = None
    prime_tower_brim_width: Optional[float] = None
    raft_contact_distance: Optional[float] = None
    raft_expansion: Optional[float] = None
    slice_closing_radius: Optional[float] = None
    staggered_inner_seams: Optional[bool] = None
    support_angle: Optional[float] = None
    thick_bridges: Optional[bool] = None
    travel_speed_z: Optional[float] = None
    tree_support_angle_slow: Optional[float] = None
    tree_support_branch_diameter_angle: Optional[float] = None
    tree_support_branch_diameter_double_wall: Optional[float] = None
    tree_support_tip_diameter: Optional[float] = None
    tree_support_top_rate: Optional[float] = None
    wall_transition_angle: Optional[float] = None
    wall_transition_filter_deviation: Optional[float] = None
    wall_transition_length: Optional[float] = None
    bottom_solid_infill_flow_ratio: Optional[float] = None
    alternate_extra_wall: Optional[bool] = None
    bridge_density: Optional[float] = None
    brim_ears_detection_length: Optional[float] = None
    brim_ears_max_angle: Optional[float] = None
    counterbore_hole_bridging: Optional[Literal['none', 'partiallybridge', 'sacrificiallayer']] = None
    detect_narrow_internal_solid_infill: Optional[bool] = None
    dont_filter_internal_bridges: Optional[Literal['disabled', 'limited', 'nofilter']] = None
    elefant_foot_compensation_layers: Optional[int] = None
    flush_into_infill: Optional[bool] = None
    flush_into_objects: Optional[bool] = None
    flush_into_support: Optional[bool] = None
    fuzzy_skin: Optional[Literal['none', 'external', 'all', 'allwalls']] = None
    fuzzy_skin_first_layer: Optional[bool] = None
    fuzzy_skin_point_distance: Optional[float] = None
    fuzzy_skin_thickness: Optional[float] = None
    gap_fill_target: Optional[Literal['everywhere', 'topbottom', 'nowhere']] = None
    gcode_add_line_number: Optional[bool] = None
    gcode_comments: Optional[bool] = None
    hole_to_polyhole: Optional[bool] = None
    hole_to_polyhole_threshold: Optional[Union[float, Percentage]] = None
    hole_to_polyhole_twisted: Optional[bool] = None
    initial_layer_min_bead_width: Optional[float] = None
    internal_bridge_flow: Optional[float] = None
    ironing_angle: Optional[float] = None
    ironing_pattern: Optional[Literal['concentric', 'zig-zag']] = None
    is_infill_first: Optional[bool] = None
    make_overhang_printable: Optional[bool] = None
    make_overhang_printable_angle: Optional[float] = None
    make_overhang_printable_hole_size: Optional[float] = None
    max_bridge_length: Optional[float] = None
    max_volumetric_extrusion_rate_slope: Optional[float] = None
    max_volumetric_extrusion_rate_slope_segment_length: Optional[int] = None
    min_length_factor: Optional[float] = None
    min_width_top_surface: Optional[Union[float, Percentage]] = None
    mmu_segmented_region_interlocking_depth: Optional[float] = None
    mmu_segmented_region_max_width: Optional[float] = None
    only_one_wall_first_layer: Optional[bool] = None
    overhang_reverse: Optional[bool] = None
    overhang_reverse_internal_only: Optional[bool] = None
    overhang_reverse_threshold: Optional[Union[float, Percentage]] = None
    overhang_speed_classic: Optional[bool] = None
    post_process: Optional[List[str]] = None
    prime_volume: Optional[float] = None
    print_flow_ratio: Optional[float] = None
    print_order: Optional[Literal['default', 'as_obj_list']] = None
    scarf_angle_threshold: Optional[int] = None
    scarf_joint_flow_ratio: Optional[float] = None
    scarf_joint_speed: Optional[Union[float, Percentage]] = None
    scarf_overhang_threshold: Optional[float] = None
    seam_slope_min_length: Optional[float] = None
    seam_slope_start_height: Optional[Union[float, Percentage]] = None
    seam_slope_steps: Optional[int] = None
    seam_slope_type: Optional[Literal['none', 'external', 'all']] = None
    single_extruder_multi_material_priming: Optional[bool] = None
    slicing_mode: Optional[Literal['regular', 'even_odd', 'close_holes']] = None
    small_area_infill_flow_compensation: Optional[bool] = None
    small_area_infill_flow_compensation_model: Optional[List[str]] = None
    solid_infill_filament: Optional[int] = None
    sparse_infill_filament: Optional[int] = None
    spiral_mode_max_xy_smoothing: Optional[Union[float, Percentage]] = None
    spiral_mode_smooth: Optional[bool] = None
    support_bottom_interface_spacing: Optional[float] = None
    support_critical_regions_only: Optional[bool] = None
    support_interface_not_for_body: Optional[bool] = None
    support_remove_small_overhang: Optional[bool] = None
    thick_internal_bridges: Optional[bool] = None
    timelapse_type: Optional[Literal['0', '1']] = None
    top_solid_infill_flow_ratio: Optional[float] = None
    tree_support_adaptive_layer_height: Optional[bool] = None
    tree_support_auto_brim: Optional[bool] = None
    tree_support_branch_angle_organic: Optional[float] = None
    tree_support_branch_diameter_organic: Optional[float] = None
    tree_support_branch_distance: Optional[float] = None
    tree_support_branch_distance_organic: Optional[float] = None
    tree_support_brim_width: Optional[float] = None
    wall_direction: Optional[Literal['auto', 'ccw', 'cw']] = None
    wall_filament: Optional[int] = None
    wipe_before_external_loop: Optional[bool] = None
    wipe_on_loops: Optional[bool] = None
    wipe_tower_bridging: Optional[float] = None
    wipe_tower_cone_angle: Optional[float] = None
    wipe_tower_extra_spacing: Optional[float] = None
    wipe_tower_rotation_angle: Optional[float] = None
    wiping_volumes_extruders: Optional[List[float]] = None
    preheat_time: Optional[float] = None
    preheat_steps: Optional[int] = None
    top_bottom_infill_wall_overlap: Optional[float] = None


class PerOverrideExplanation(BaseModel):
    parameter: str = Field(description="Human readable name of the parameter that was changed")
    explanation: str = Field(description="A concise explanation of why the parameter was changed")


class SlicingResponse(BaseModel):
    overall_explanation: str = Field(
        description=dedent("""
            A response to the user's request, describing how the user's request was handled.
            **Important**:
            - Avoid referring to 'the user' and speak naturally.
            - Avoid revealing your internal logic.
        """)
    )
    filament_param_override: Optional[FilamentParamOverride] = Field(
        default=None,
        description="Override values for filament-related parameters like temperature, flow rate, and cooling settings"
    )
    print_process_param_override: Optional[PrintProcessParamOverride] = Field(
        default=None,
        description="Override values for print process parameters like layer height, speed, and support settings"
    )
    per_override_explanations: Optional[List[PerOverrideExplanation]] = Field(
        default=None,
        description="A list of explanations for each parameter override"
    )

    @field_validator(
        "filament_param_override",
        "print_process_param_override",
        "per_override_explanations",
        mode="before",
    )
    @staticmethod
    def _parse_json_string_fields(v):
        return parse_json_string_fields(v)


def fix_filament_param_override(filament_param_override):
    if filament_param_override is None:
        return None

    result = {}
    for key, value in filament_param_override.items():
        final_value = None
        if isinstance(value, list):
            if len(value) == 1:
                final_value = value[0]  # Use the single element directly
            else:
                sentry_sdk.capture_message(f"filament_param_override is a list but does not have a single element: {key}")
        else:
            final_value = value

        final_value = fix_boolean_param_value(final_value)
        result[key] = [final_value]

    return result

def fix_print_process_param_override(print_process_param_override):
    if print_process_param_override is None:
        return None

    result = {}
    for key, value in print_process_param_override.items():
        final_value = value
        final_value = fix_boolean_param_value(final_value)
        result[key] = final_value

    return result

def fix_support_related_param_override(print_process_param_override):
    if print_process_param_override is None:
        return None

    SUPPORT_PARAM_KEYS = [
        'tree_support_adaptive_layer_height',
        'tree_support_auto_brim',
        'tree_support_branch_angle_organic',
        'tree_support_branch_diameter_organic',
        'tree_support_branch_distance',
        'tree_support_branch_distance_organic',
        'tree_support_brim_width',
        'support_bottom_interface_spacing',
        'support_critical_regions_only',
        'support_interface_not_for_body',
        'support_remove_small_overhang',
        'support_angle',
        'tree_support_angle_slow',
        'tree_support_branch_diameter_angle',
        'tree_support_branch_diameter_double_wall',
        'tree_support_tip_diameter',
        'tree_support_top_rate',
        'support_expansion',
        'tree_support_branch_diameter',
        'tree_support_with_infill',
        'support_interface_pattern',
        'support_type',
        'support_style',
        'support_interface_bottom_layers',
        'tree_support_branch_angle',
        'tree_support_wall_count',
        'support_filament',
        'support_line_width',
        'support_interface_filament',
        'support_on_build_plate_only',
        'support_top_z_distance',
        'support_interface_loop_pattern',
        'support_interface_top_layers',
        'support_interface_spacing',
        'support_interface_speed',
        'support_base_pattern',
        'support_base_pattern_spacing',
        'support_speed',
        'support_threshold_angle',
        'support_object_xy_distance',
    ]

    should_enable_support = any(key in SUPPORT_PARAM_KEYS for key in print_process_param_override)
    if should_enable_support:
        print_process_param_override['enable_support'] = 1

    return print_process_param_override

def fix_brim_related_param_override(print_process_param_override):
    if print_process_param_override is None:
        return None

    BRIM_PARAM_KEYS = [
        'brim_type',
        'brim_width',
        'brim_object_gap',
        'brim_ears_max_angle',
        'brim_ears_detection_length',
    ]

    should_enable_brim = any(key in BRIM_PARAM_KEYS for key in print_process_param_override)
    if should_enable_brim and print_process_param_override.get('brim_type', 'auto_brim') == 'auto_brim':
        print_process_param_override['brim_type'] = 'outer_and_inner' # "auto" does not guarantee brim

    return print_process_param_override


def fix_boolean_param_value(value): # OrcaSlicer takes 1 or 0, not true or false
    if isinstance(value, bool):
        return 1 if value else 0
    return value

def adjustments_system_prompt(print_process_preset_name, filament_params, print_process_params, language_rule):
    return dedent(f"""
        You are a 3D printing expert assistant. Your role is to help users optimize
        their 3D printing parameters based on their specific needs and queries.

        Current settings:
        - Print process preset: {print_process_preset_name}
        - Filament parameters: {filament_params}
        - Print process parameters: {print_process_params}

        Instructions:
        1. Analyze the current parameters and determine if they are optimal for the user's requirements.
        2. If they are not optimal, determine which parameters need to be changed and why. These are called "parameter overrides".

        Important:
        - For each parameter override, you MUST provide a concise explanation of why it was needed.

        {language_rule}
    """)


def determine_slicing_settings_adjustments_step(chat, print_process_preset_name, preset_explanation, openai_client):
    instructor_client = instructor.from_openai(openai_client)
    slicing_params = chat.get('slicing_profiles', {})

    filament_preset = slicing_params.get('filament_presets', [])[0] # We assume that only the selected filament preset is in the request. This may change in the future.
    prev_filament_overrides = slicing_params.get('filament_overrides', {})
    filament_params = combined_params(filament_preset['config'], prev_filament_overrides)

    print_process_presets = slicing_params.get('print_process_presets', [])
    suggested_print_process_preset = next(
        (preset for preset in print_process_presets if preset.get('name') == print_process_preset_name),
        None
    )

    prev_print_process_preset_name = next(
        (preset.get('name') for preset in slicing_params.get('print_process_presets', []) if preset.get('is_selected')),
        None
    )
    same_preset = prev_print_process_preset_name == print_process_preset_name

    if same_preset:
        prev_print_process_overrides = slicing_params.get('print_process_overrides', {})
    else:
        prev_print_process_overrides = {}

    from ..language_utils import get_response_language_rule

    print_process_params = combined_params(suggested_print_process_preset, prev_print_process_overrides)
    language_rule = get_response_language_rule(chat)

    system_prompt = adjustments_system_prompt(
        print_process_preset_name=print_process_preset_name,
        filament_params=filament_params,
        print_process_params=print_process_params,
        language_rule=language_rule,
    )

    chat_history = chat.get('messages', [])
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    response = instructor_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        response_model=SlicingResponse
    )

    filtered_response = response.model_dump(exclude_none=True)

    per_override_explanations = filtered_response.get('per_override_explanations', [])

    if per_override_explanations and not same_preset: # Overrides were made and preset has changed
        combined_explanation = combine_explanations(chat, prev_print_process_preset_name, print_process_preset_name, preset_explanation, filtered_response.get('overall_explanation', ''), openai_client)
    else:
        combined_explanation = filtered_response.get('overall_explanation', '') if same_preset else preset_explanation

    filament_overrides = filtered_response.get('filament_param_override', {})
    print_process_overrides = filtered_response.get('print_process_param_override', {})

    filament_overrides = fix_filament_param_override(filament_overrides)

    print_process_overrides = fix_print_process_param_override(print_process_overrides)
    print_process_overrides = fix_support_related_param_override(print_process_overrides)
    print_process_overrides = fix_brim_related_param_override(print_process_overrides)

    # Final overrides are the new overrides on top of the previous overrides
    prev_filament_overrides = fix_filament_param_override(prev_filament_overrides) # TODO: Fix this mess
    final_filament_overrides = combined_params(prev_filament_overrides, filament_overrides)
    final_print_process_overrides = combined_params(prev_print_process_overrides, print_process_overrides)

    return {
        "message": {
            "role": "assistant",
            "content": combined_explanation,
            "per_override_explanations": per_override_explanations,
            "slicing_profiles": {
                "use_print_process_preset": print_process_preset_name,
                "filament_overrides": final_filament_overrides,
                "print_process_overrides": final_print_process_overrides
            }
        }
    }


def combine_explanations(chat, prev_preset_name, preset_name, preset_explanation, adjustments_explanation, openai_client):
    from ..language_utils import get_response_language_rule

    language_rule = get_response_language_rule(chat)
    system_prompt = dedent(f"""
        You are a 3D printing expert assistant. Your role is to combine the explanations of the previous steps into a single, coherent paragraph.

        Below are the response in previous steps:
        Step 1 has change the print process preset from "{prev_preset_name}" to "{preset_name}" with the following explanation:
        "{preset_explanation}"
        Step 2 may or may not have made adjustments to the slicing parameters, with the following explanation:
        "{adjustments_explanation}"

        Important:
        - Avoid referring to 'the user' and speak naturally.
        - Avoid revealing your internal logic.
        - Use less than 80 words.

        {language_rule}
    """)


    chat_history = chat.get('messages', [])
    chat_history = [chat_history[-1]] if chat_history else []
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(chat_history)

    response = openai_client.chat.completions.create(
        model=os.environ.get('LLM_MODEL_NAME'),
        messages=messages,
        temperature=0.0,
    )

    return response.choices[0].message.content