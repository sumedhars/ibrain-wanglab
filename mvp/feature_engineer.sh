#!/bin/bash
#SBATCH --job-name=WangLab            # Job name
#SBATCH --output=output_%j.txt        # Standard output file
#SBATCH --error=error_%j.txt          # Standard error file
#SBATCH --nodes=1                     # Number of nodes
#SBATCH --partition=teaching
#SBATCH --gres=gpu:t4:1
#SBATCH --ntasks-per-node=1           # Number of tasks per node
#SBATCH --cpus-per-task=2             # Number of CPU cores per task
#SBATCH --time=3-00:00:00             # Maximum runtime (D-HH:MM:SS)
#SBATCH --mail-type=END               # Send email at job completion
#SBATCH --mail-user=kirkpatricki@msoe.edu    # Email address for notifications
#SBATCH --account=practicum

#Load necessary modules (if needed)
#module load module_name

#Your job commands go here
#For example:
# srun python3 ./new_split_rois.py
srun python3 ./Test_FE.py
