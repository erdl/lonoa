#offline egauge
#python3 egauge_api.py 1526548513 1526549515 34111 ~/Projects/egauge/output.csv
#online egauge
python3 egauge_api.py 1526548513 1526549515 725 ./test_egauge_api_01.output.expected.log
#diff test_egauge_api_01_output.log test_egauge_api_01.log
./test_egauge_api_01.output.expected.log ./test_egauge_api_01.output.log
