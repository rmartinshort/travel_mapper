# Run the UI
# run this from the top level directory of the travel mapper project
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "Starting travel mapper UI"
$(pwd)/travel_mapper/user_interface/driver.py