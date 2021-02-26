set current_dir = %cd%
set PyMyoVent_dir = "c:\ken\github\campbellmusclelab\models\pymyovent\python_code"

cd PyMyoVent_dir
python pymyovent.py run_batch batch.json
cd current_dir

