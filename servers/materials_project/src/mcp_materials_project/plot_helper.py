import crystal_toolkit.components as ctc
import numpy as np
import plotly.graph_objects as go
from pymatgen.core.structure import Structure


def draw_cone(fig, start, end, radius=0.1, segments=16, color="gray"):
    """
    Draw a cone in plotly figure.

    Args:
        fig: plotly figure object
        start: starting point of the cone (base center)
        end: end point of the cone (tip)
        radius: radius of the cone base
        segments: number of segments for the cone base circle
        color: color of the cone
    """
    # Convert to numpy arrays for easier calculation
    start = np.array(start)
    end = np.array(end)

    # Calculate direction vector and length
    direction = end - start
    length = np.linalg.norm(direction)
    if length == 0:
        return

    # Normalize direction vector
    direction = direction / length

    # Find perpendicular vectors to create the base circle
    if abs(direction[2]) < 0.9:
        perpendicular = np.cross(direction, [0, 0, 1])
    else:
        perpendicular = np.cross(direction, [1, 0, 0])
    perpendicular = perpendicular / np.linalg.norm(perpendicular)
    perpendicular2 = np.cross(direction, perpendicular)

    # Create points for the base circle
    theta = np.linspace(0, 2 * np.pi, segments)
    circle_points = []
    for t in theta:
        point = start + radius * \
            (np.cos(t) * perpendicular + np.sin(t) * perpendicular2)
        circle_points.append(point)

    # Add the tip point
    circle_points.append(circle_points[0])  # Close the base

    # Create triangular faces
    for i in range(segments):
        # Add a triangular face
        fig.add_trace(
            go.Mesh3d(
                x=[circle_points[i][0], circle_points[i + 1][0], end[0]],
                y=[circle_points[i][1], circle_points[i + 1][1], end[1]],
                z=[circle_points[i][2], circle_points[i + 1][2], end[2]],
                i=[0],
                j=[1],
                k=[2],
                color=color,
                opacity=0.8,
            )
        )

    # Add the base
    fig.add_trace(
        go.Mesh3d(
            x=[p[0] for p in circle_points],
            y=[p[1] for p in circle_points],
            z=[p[2] for p in circle_points],
            i=list(range(segments - 1)),
            j=list(range(1, segments)),
            k=[segments - 1] * (segments - 1),
            color=color,
            opacity=0.8,
        )
    )


def draw_axis(fig, start, direction, length, color, label, line_width=12, arrow_length=0.4, arrow_radius=0.1):
    """
    Draw an axis with a cone-shaped arrow and label.

    Args:
        fig: plotly figure object
        start: starting point of the axis
        direction: direction vector of the axis
        length: total length of the axis
        color: color of the axis and arrow
        label: text label for the axis
        line_width: width of the axis line
        arrow_length: length of the arrow cone
        arrow_radius: radius of the arrow cone base
    """
    # Normalize direction vector
    direction = np.array(direction)
    direction = direction / np.linalg.norm(direction)

    # Calculate end points
    end = np.array(start) + direction * length
    # Where the line ends and arrow begins
    line_end = end - direction * arrow_length

    # Draw the main axis line
    fig.add_trace(
        go.Scatter3d(
            x=[start[0], line_end[0]],
            y=[start[1], line_end[1]],
            z=[start[2], line_end[2]],
            mode="lines",
            line=dict(color=color, width=line_width),
            showlegend=False,
        )
    )

    # Draw the arrow cone
    draw_cone(fig, start=line_end, end=end, radius=arrow_radius, color=color)

    # Add label with small offset
    label_offset = 0.2
    label_pos = end + direction * label_offset
    fig.add_trace(
        go.Scatter3d(
            x=[label_pos[0]],
            y=[label_pos[1]],
            z=[label_pos[2]],
            mode="text",
            text=[label],
            textposition="middle center",
            showlegend=False,
        )
    )


def convert_scene_to_plotly(scene_data, structure, bond_width=12, axes_width=12, axis_displacement=0.5):
    fig = go.Figure()

    # Add atoms (spheres)
    atoms_content = next(
        (item["contents"] for item in scene_data["contents"] if item["name"] == "atoms"), [])

    # Calculate the range for each axis including all points
    all_points = []
    for atom in atoms_content:
        all_points.extend(atom["positions"])

    axis_origin = [0, 0, 0]
    x_coords = [p[0] for p in all_points]
    y_coords = [p[1] for p in all_points]
    z_coords = [p[2] for p in all_points]
    # Get lattice vectors
    lattice = structure.lattice
    a_vector = lattice.matrix[0]
    b_vector = lattice.matrix[1]
    c_vector = lattice.matrix[2]

    displacement = -axis_displacement * (a_vector + b_vector + c_vector)

    x_coords.append(axis_origin[0] + displacement[0])
    y_coords.append(axis_origin[1] + displacement[1])
    z_coords.append(axis_origin[2] + displacement[2])
    x_coords.append(a_vector[0])
    y_coords.append(a_vector[1])
    z_coords.append(a_vector[2])
    x_coords.append(b_vector[0])
    y_coords.append(b_vector[1])
    z_coords.append(b_vector[2])
    x_coords.append(c_vector[0])
    y_coords.append(c_vector[1])
    z_coords.append(c_vector[2])

    x_range = [min(x_coords), max(x_coords)]
    y_range = [min(y_coords), max(y_coords)]
    z_range = [min(z_coords), max(z_coords)]

    x_size = x_range[1] - x_range[0]
    y_size = y_range[1] - y_range[0]
    z_size = z_range[1] - z_range[0]

    eps = 0.1

    x_range = [x_range[0] - eps * x_size, x_range[1] + eps * x_size]
    y_range = [y_range[0] - eps * y_size, y_range[1] + eps * y_size]
    z_range = [z_range[0] - eps * z_size, z_range[1] + eps * z_size]

    # Calculate aspect ratios normalized to the largest dimension
    max_size = max(x_size, y_size, z_size)
    x_ratio = x_size / max_size
    y_ratio = y_size / max_size
    z_ratio = z_size / max_size

    # Calculate scaling factor for sphere sizes based on structure size
    structure_size = min(x_size, y_size, z_size)
    # Adjust this divisor to make spheres larger or smaller
    sphere_scale_factor = structure_size * 3

    for atom in atoms_content:
        positions = atom["positions"]
        color = atom["color"]
        radius = atom["radius"]
        tooltip = atom["tooltip"]

        fig.add_trace(
            go.Scatter3d(
                x=[pos[0] for pos in positions],
                y=[pos[1] for pos in positions],
                z=[pos[2] for pos in positions],
                mode="markers",
                marker=dict(
                    size=radius * sphere_scale_factor,  # Scale the radius by the structure size
                    color=color,
                    symbol="circle",
                ),
                name=tooltip.split()[0],
                text=[tooltip],
                hoverinfo="text",
            )
        )

    # Add unit cell
    unit_cell_content = next(
        (item["contents"] for item in scene_data["contents"] if item["name"] == "unit_cell"), [])

    if unit_cell_content:
        cell_lines = unit_cell_content[0]["contents"][0]["positions"]
        for i in range(0, len(cell_lines), 2):
            start = cell_lines[i]
            end = cell_lines[i + 1]
            fig.add_trace(
                go.Scatter3d(
                    x=[start[0], end[0]],
                    y=[start[1], end[1]],
                    z=[start[2], end[2]],
                    mode="lines",
                    line=dict(color="black", width=2),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    # Add bonds
    bonds_content = next(
        (item["contents"] for item in scene_data["contents"] if item["name"] == "bonds"), [])
    # logger.info(bonds_content)

    for bond in bonds_content:
        positions = bond["positions"]
        for i in range(0, len(positions), 2):
            start = positions[i]
            end = positions[i + 1]

            # Draw the main bond line
            fig.add_trace(
                go.Scatter3d(
                    x=[start[0], end[0]],
                    y=[start[1], end[1]],
                    z=[start[2], end[2]],
                    mode="lines",
                    line=dict(color="gray", width=bond_width),
                    showlegend=False,
                )
            )

    # Draw the axes
    draw_axis(
        fig,
        axis_origin + displacement,
        a_vector,
        np.linalg.norm(a_vector) * axis_displacement,
        "red",
        "a",
        line_width=axes_width,
    )
    draw_axis(
        fig,
        axis_origin + displacement,
        b_vector,
        np.linalg.norm(b_vector) * axis_displacement,
        "green",
        "b",
        line_width=axes_width,
    )
    draw_axis(
        fig,
        axis_origin + displacement,
        c_vector,
        np.linalg.norm(c_vector) * axis_displacement,
        "blue",
        "c",
        line_width=axes_width,
    )

    # Update layout
    fig.update_layout(
        scene=dict(
            aspectmode="manual",  # Ensure equal scaling
            aspectratio=dict(x=x_ratio, y=y_ratio, z=z_ratio),
            xaxis=dict(
                showbackground=False,
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showaxeslabels=False,
                title="",  # Remove axis title
                visible=False,  # Hide axis completely
                range=x_range,  # Set explicit range
            ),
            yaxis=dict(
                showbackground=False,
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showaxeslabels=False,
                title="",  # Remove axis title
                visible=False,  # Hide axis completely
                range=y_range,  # Set explicit range
            ),
            zaxis=dict(
                showbackground=False,
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks="",
                showticklabels=False,
                showaxeslabels=False,
                title="",  # Remove axis title
                visible=False,  # Hide axis completely
                range=z_range,  # Set explicit range
            ),
            camera=dict(
                # Set projection to orthographic
                projection=dict(type="orthographic"),
                eye=dict(x=1.5, y=-1.5, z=0),
            ),
            bgcolor="white",
            annotations=[],  # Remove any automatic annotations
        ),
        width=600,  # Set figure width
        height=400,  # Set figure height
        # Reduce margins to maximize plot area
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            x=1.0,
            y=0.0,
            xanchor="right",
            yanchor="bottom",
            itemsizing="constant",
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="lightgray",
            borderwidth=1,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def plot_structure(structure: Structure, duplication: list[int] = [1, 1, 1]):
    """
    Get the plotly figure for a given structure file

    Args:
        material_id: Materials Project Structure object
    Returns:
        plotly figure object or error message
    """
    structure = structure * duplication
    # Create structure component
    structure_component = ctc.StructureMoleculeComponent(
        structure, id="structure")

    # Get scene data
    graph = structure_component._preprocess_input_to_graph(
        structure, bonding_strategy="CutOffDictNN", bonding_strategy_kwargs={}
    )

    scene, legend = structure_component.get_scene_and_legend(
        graph,
        color_scheme="VESTA",
        radius_strategy="uniform",
        draw_image_atoms=True,
        bonded_sites_outside_unit_cell=True,
        hide_incomplete_bonds=False,
    )

    # Convert scene to plotly figure
    fig = convert_scene_to_plotly(scene, structure)
    return fig
