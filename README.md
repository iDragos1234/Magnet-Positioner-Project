# Magnet Positioner

## Introduction

Repository for the course _QIST4500 Multidisciplinary Team Project_.
In this course, our team had the task of building a gantry system used in positioning an external permanent magnet, adapted to a certain model of dilution refrigerator.
This magnet is intended for quantum control of qubits inside the refrigerator, potentially achieving this without the superconducting coil inside the refrigerator giving a static uniaxial magnetic field $B_z$ [1].
The advantage of this method is that it saves more space inside the refrigerator, allowing for more electronics and wiring to be fitted inside the refrigerator [1]. 
Another advantage is that the direction of the magnetic field $B_z$ can be changed [1]. 
In hybrid operating mode (i.e., using both the external and the internal magnet), it was experimentally shown that this could result in increased coherence times over the internal-magnet-only operating mode, while single-qubit gate fidelities stay below the fault-tolerant threshold for quantum error correction [1].


## Contents

* `magnet_positioner_cad_design/`: Folder containing all CAD files for the magnet positioning system, including a STEP file of the whole assembly.

* `magnet_xyz_positioner_code/`: Code used to control the motors. Largely unchanged from the initial code given to us.

* `magnet_data/`: Magnet measurement used for motor calibration and mapping the magnetic field. At the moment, only measurements along the x-axis are included, on a 1D grid with 1 cm spacing between neighbouring points.

* `documents/`: Relevant documents for this project, including the final report and final presentation for this project.

* `magnet_simulation.ipynb/`: Magnetic field simulations with Magpylib of the magnet used in our project.

*  `plot_magnet_data.py`: Plot of the measurements in `magnet_data/`.


## References

[1] Yu, Cecile X., et al. "Optimising germanium hole spin qubits with a room-temperature magnet." arXiv preprint arXiv:2507.03390 (2025).
