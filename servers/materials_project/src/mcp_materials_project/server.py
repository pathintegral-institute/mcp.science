import base64
from typing import Literal

from emmet.core.bonds import List
from emmet.core.summary import SummaryDoc
from loguru import logger
from mcp.server.fastmcp import FastMCP
from mcp.types import EmbeddedResource, ImageContent, TextContent, TextResourceContents
from pymatgen.io.ase import AseAtomsAdaptor

from .data_class import StructureData, SupercellParameters
from .structure_helper import (
    get_structure_from_material_id,
    get_structure_info,
    get_structure_folder_path,
)
from .rester import mp_rester
from .moire_helper import homobilayer_twist


mcp = FastMCP("mcp-materials-project")


@mcp.tool()
async def search_materials_by_formula(chemical_formula: str) -> list[str]:
    """
    Search for materials in the MPRester database by chemical formula

    Args:
        chemical_formula: the chemical formula of the material

    Returns:
        a list of TextContent objects, each TextContent object contains the
        description of a structure with the given chemical formula
    """

    search_results: list[SummaryDoc] = mp_rester.summary.search(
        formula=chemical_formula)
    structure_description_list: list[str] = []
    for search_result in search_results:
        structure_data = StructureData(material_id=search_result.material_id)
        structure_description_list.append(structure_data.description)

    return structure_description_list


@mcp.tool()
async def select_material_by_id(material_id: str) -> list[TextContent]:
    """
    Select a material from a list of structure_info objects by material_id

    Args:
        material_id: the id of the material

    Returns:
        A list that contains two elements. The first element is
        the TextContent that contains the description of the structure. The second element
        is the TextContent that contains the uri of the structure.
    """
    structure_data = get_structure_from_material_id(material_id)
    structure_uri = f"structure://{structure_data.structure_id}"
    response = [TextContent(type="text", text=structure_data.description)]
    response.append(TextContent(
        type="text", text="structure uri: " + structure_uri))
    return response


@mcp.tool()
async def get_structure_data(
    structure_uri: str,
    format: Literal["cif", "poscar"] = "poscar",
) -> list[TextContent]:
    """
    Obtain the structure data (coordinates of atoms and other properties of the bulk or supercell crystal structure)

    Args:
        structure_uri: the uri of the structure
        format: the format of the structure file, could be poscar or cif.

    Returns
        the structure file content as a string
    """
    structure_data = get_structure_info(structure_uri)
    if structure_data is None:
        return [TextContent(type="text", text="Structure not found")]

    if format == "cif":
        structure_str = structure_data.structure.to(fmt="cif")
    elif format == "poscar":
        structure_str = structure_data.poscar_str

    return [TextContent(type="text", text=structure_str)]


@mcp.tool()
async def create_structure_from_poscar(poscar_str: str) -> list[TextContent]:
    """
    Create a new structure from a poscar string

    Args:
        poscar_str: the poscar string of the structure

    Returns:
        A list that contains a single element. The element is a TextContent
        that contains the description of the new structure.
    """
    structure_data = StructureData(structure=poscar_str)
    structure_id = structure_data.structure_id
    structure_uri = f"structure://{structure_id}"
    structure_folder_path = get_structure_folder_path(structure_uri)
    structure_data.to_folder(structure_folder_path)
    response = [TextContent(
        type="text", text=f"A new structure is created with the structure uri: {structure_uri}")]
    response.append(TextContent(type="text", text=structure_data.description))
    return response


@mcp.tool()
async def plot_structure(
    structure_uri: str, duplication: list[int] = [1, 1, 1]
) -> list[ImageContent | TextContent | EmbeddedResource]:
    """
    Plot the structure of a material

    Args:
        structure_uri: the uri of the structure
        duplication: the duplication of the structure in the plot, specified by a list of three integers along a,b,c axis.

    Returns:
        The ImageContent that contains the PNG image of the requested structure"""

    structure_data = get_structure_info(structure_uri)
    if structure_data is None:
        return [TextContent(type="text", text="Structure not found")]

    fig = structure_data.plot_structure_ct(duplication=[1, 1, 1])
    img_bytes = fig.to_image(format="png", scale=1)
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    return [
        ImageContent(
            type="image", data=img_base64, mimeType="image/png"),
        EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri=structure_uri, text=fig.to_json(), mimeType="application/json"),
            # EmbeddedResource has enabled extra fields, so add an extra_type to indicate it's a plotly figure
            extra_type="plotly",  # type: ignore
        ),
    ]


@mcp.tool()
async def build_supercell(bulk_structure_uri: str, supercell_parameters: SupercellParameters) -> list[TextContent]:
    """
    Starting from a bulk_structure in structure_info, build a supercell structure and store it into a new structure_info

    Args:
        structure_uri: the uri of the bulk structure
        supercell_parameters: a dictionary containing the supercell parameters

    Returns:
        A list that contains a single element. The element is a TextContent
        that contains the description of the updated bulk and supercell structure."""
    bulk_structure_data = get_structure_info(structure_uri=bulk_structure_uri)
    if bulk_structure_data is None:
        response = TextContent(type="text", text="Bulk structure not found")
        return [response]
    supercell_structure_data = StructureData.build_supercell(
        bulk_structure_data=bulk_structure_data, supercell_parameters=supercell_parameters
    )
    # save the updated structure info in the folder
    supercell_structure_uri = f"structure://{supercell_structure_data.structure_id}"
    supercell_structure_folder_path = get_structure_folder_path(
        supercell_structure_uri)
    supercell_structure_data.to_folder(supercell_structure_folder_path)

    return [
        TextContent(
            type="text", text=f"Supercell structure is created with the structure uri: {supercell_structure_uri}"
        ),
        TextContent(
            type="text", text=f"Description of the supercell structure: {supercell_structure_data.description}")
    ]


@mcp.tool()
async def moire_homobilayer(
    bulk_structure_uri: str,
    interlayer_spacing: float,
    max_num_atoms: int = 10,
    twist_angle: float = 0.0,
    vacuum_thickness: float = 15.0,
) -> List[TextContent]:
    """
    Generate a moire superstructure of a 2D homobilayer and save it to folder, retrievable by a structure_uri
    Args:
        bulk_structure_uri (str): the uri of the bulk structure used to build the moire bilayer
        interlayer_spacing (float): The interlayer spacing between the two layers, in angstrom.
        max_num_atoms (int): The maximum number of atoms in the moire superstructure.
        twist_angle (float): The twist angle of the moire superstructure, in degrees.
        vacuum_thickness (float): The vacuum thickness in the z direction, in angstrom.
    Returns:
        The text response that contains the structure_uri of the moire structure
    """
    adaptor = AseAtomsAdaptor()
    bulk_structure_data = get_structure_info(structure_uri=bulk_structure_uri)
    bulk_atoms = adaptor.get_atoms(structure=bulk_structure_data.structure)
    moire_atoms = homobilayer_twist(
        structure=bulk_atoms,
        interlayer_spacing=interlayer_spacing,
        max_num_atoms=max_num_atoms,
        twist_angle=twist_angle,
        vacuum_thickness=vacuum_thickness,
    )

    moire_structure = adaptor.get_structure(moire_atoms)
    moire_structure_data = StructureData(structure=moire_structure)
    moire_structure_data.parent_ids = [bulk_structure_data.structure_id]
    moire_structure_uri = f"structure://{moire_structure_data.structure_id}"
    moire_structure_folder_path = get_structure_folder_path(
        moire_structure_uri)
    moire_structure_data.to_folder(moire_structure_folder_path)
    return [TextContent(type="text", text=f"Moire structure is created with the structure uri: {moire_structure_uri}")]
