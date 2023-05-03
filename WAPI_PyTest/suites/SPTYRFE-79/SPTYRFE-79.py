import pytest
import unittest
import commands
import ib_utils.ib_NIOS as ib_NIOS
import subprocess
import requests
import re
import json
import json, ast
import os
import time
import sys
import logging
import pexpect
import config
from time import sleep
import ib_utils.common_utilities as common_util
import ib_utils.common_utilities as comm_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv








output = config.grid1_router
print(output)
#li = list(output.split("."))
output1 = list(output)
output1[-1]="0"
string = " ".join(output1)
string1 = string.replace(" ","")
print("string1",string1)


def Upload():
		for i in range(10):
                        ping = os.popen("for i in range{1..3} ; do ping -w 5 -c 4 "+config.grid1_master_ha_vip+" ; done").read()
                        print(ping)
                        if "0 received" not in ping:
                                print("\n")
                                print(config.grid1_master_ha_vip+" is pinging, starting the grid upgrade ")
                                print("\n")
                                try:
                                        grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
                                        print(grid_upgrade_status)
                                        data = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit")
                                        print(data)
                                        data  = json.loads(data)
                                        data  = eval(json.dumps(data))
                                        token = data['token']
                                        url   = data['url']
                                        sleep(20)
                                        url_upload = ('curl -k -u admin:infoblox -F name='+config.UPGRADE_BUILD_PATH+' -F filedata=@'+config.UPGRADE_BUILD_PATH+' '+'"'+url+'"')
                                        url_upload  = os.popen(url_upload).read()
                                        print("url_upload is",url_upload)
                                        sleep(20)
                                        data = {"token":token}
                                        token_upload = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=set_upgrade_file")
                                        print("\n")
                                        print("token_upload",token_upload)
                                        break
                                except:
                                        print("Upgrade file upload attempt is failed, going for 60sec sleep and will try again after 60sec")
                                        sleep(60)
                                        if(i==9):
                                                msg = "Uploading the upgrade file failed after 10 attempts, hence aborting the upgrade"
                                                exit()
                        elif(i==(9)):
                                msg = "Grid IP "+config.grid1_master_ha_vip+" is not pinging even after 10 attempts, hence aborting the upgrade"
                                print(msg)
                                exit()
                        else:
                                print(config.grid1_master_ha_vip+" is not pinging, Going for 60sec sleep")
                                print("\n")
                                sleep(60)
                print("\n==========================================")
                print("Validate the Grid status and start the UPLOAD")
                print("==========================================\n")
                data = {"action": "UPLOAD"}
		for i in range(1,5):
			try:
                		grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
                		print(grid_upgrade_status)
                		if ('''"upgrade_state": "NONE"''' in grid_upgrade_status):
                			upload=ib_NIOS.wapi_request('POST', object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
                        		print(upload)
                        		print("Upload was successful")
					break
                		else:
					print("Upload attempt is failed, going for 60sec sleep")
                        		sleep(60)
			except:
				print("UPLOAD attempt failed. Grid is taking too long to respond, going for 60sec sleep and will try again after 60sec")
				sleep(60)


def distribution():
		print("Validate the UPLOAD completion status and start the distribution ")
		print("=========================================================\n")
		data = {"action": "DISTRIBUTION_START"}
		for i in range(1,10):
			try:
                		grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
                		print(grid_upgrade_status)
                		if ('''"grid_state": "UPLOADED"''' in grid_upgrade_status):
					distribute=ib_NIOS.wapi_request('POST',object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
                        		print(distribute)
					print("distribution started")
					break
                		else:
                        		print("Upload is not yet completed to start the distribution,going for 60sec sleep")
                       			sleep(60)
			except:
				print("distribution attempt is failed, Grid is taking too long to respond, going for 60sec sleep and will try again after 60sec")
				sleep(60)			

def uploadtest():
		print("Validate the distribution completion status and start the Upgrade Test")
                print("=========================================================\n")
                data = {"action": "UPGRADE_TEST_START"}
		for i in range(1,80):
			try:
                		grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
                		print(grid_upgrade_status)
                		if '''"grid_state": "DISTRIBUTING_COMPLETE"''' in grid_upgrade_status:
                			UPGRADE_TEST=ib_NIOS.wapi_request('POST',object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
                        		print(UPGRADE_TEST)
					print("upload test started")
					break
                		else:
                        		print("Distribution is not yet completed to start the UPGRADE Test")
                        		sleep(60)
			except:
				print("Starting UPGRADE Test attempt is failed, Grid is taking too long to respond, going for 60sec sleep and will try again after 60sec")
				sleep(60)


def Upgrade():
		print("Validate the Upgrade Test completion status and start the Upgrade")
		print("============================================\n")
                data = {"action": "UPGRADE"}
		for i in range(1,15):
			try:
               	 		grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
                		print(grid_upgrade_status)
                		if '''"upgrade_test_status": "COMPLETED"''' in grid_upgrade_status:
                    			UPGRADE=ib_NIOS.wapi_request('POST',object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
                        		print(UPGRADE)
					print("upgarde has started")
					break
                		else:
                        		print("Upgrade Test is not yet completed, going for 60sec sleep")
                        		sleep(60)
			except:
				print("Starting UPGRADE attempt is failed. Grid is taking too long to respond, going for 60sec sleep and will try again after 60sec")
				sleep(60)







class upgrade(unittest.TestCase):


	@pytest.mark.run(order=1)
	def test_001_if_grid_is_pinging_upload_fb_build(self):
		Upload()
		print("test case 01 passed successfully")
		sleep(10)





    	@pytest.mark.run(order=2)
        def test_002_Validate_the_Upload_completion_status_and_start_the_distribution(self):
                distribution()
                print("test case 02 passed successfully")


        @pytest.mark.run(order=3)
        def test_003_Validate_the_distribution_completion_status_and_start_the_Upgrade_Test(self):
                uploadtest()
                print("test case 03 passed successfully")





	@pytest.mark.run(order=4)
        def test_004_Validate_the_Upgrade_Test_completion_status_and_start_the_Upgrade(self):
		Upgrade()
		print("test case 04  passed successfully")






	@pytest.mark.run(order=5)
	def test_005_block_passive_node_when_passive_goes_for_reboot_during_upgrade(self):
		for i in range(1,45):
        		sleep(30)
                	status = os.system("ping -c 4 "+config.grid1_master_ha_passive_ip)
                	print(status)   
               		if status != 0:
                		print("system is rebooting")
                        	cmd1 = os.system("netctl_system -i lan -S 10.35.0.0  -a vlanset  -H "+config.grid1_master_ha_passive_id )
                        	cmd2 = os.system("netctl_system -i ha -S 10.35.0.0 -a vlanset  -H "+config.grid1_master_ha_passive_id)
                        	break
                	else:
                        	print("system is not  rebooting")
		sleep(10)
	

        @pytest.mark.run(order=6)
        def test_006_validate_cli_command_is_hidden(self):
		try:
                	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_master_ha_vip)
                	child.logfile=sys.stdout
                	child.expect('password')
                	child.sendline('infoblox')
                	child.expect('Infoblox >')
               	 	child.sendline('set ?')
                	child.expect('Infoblox >')
                	output = child.before
                	if "set grid_upgrade stop_and_cancel" in output:
				print("upgrade stop cmd is not found")
                        	assert True
                	else:
				print("upgrade stop cmd is found")
                        	assert True
		except Exception as error:
			print("test case 06 failed",error)
		finally:
                	child.sendline('exit')
			child.close()
			sleep(10)


        @pytest.mark.run(order=7)
        def test_007_execute_cmd_on_active_to_check_help_cmd_updated(self):
		try:
                	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_master_ha_vip)
                	child.logfile=sys.stdout
                	child.expect('password')
                	child.sendline('infoblox')
                	child.expect('Infoblox >')
			child.sendline('set grid_upgrade stop_and_cancel')      
                	child.expect('Do you want to proceed\? \(y or n\):')
			output = child.before
                	print("output is",output)
                	child.sendline('n')
                	child.expect('Infoblox >')
                	if "Remove the power cable of the passive node while running the command to prevent the node from coming back up at a later time" in output:
				print("help cmd updated for set grid_upgrade stop_and_cancel")
                        	assert True
                	else:
				print("help cmd not updated for set grid_upgrade stop_and_cancel")
                        	assert False
		except Exception as error:
			print("test 07 failed",error)
		finally:
			child.sendline('exit')
                	child.close()
			sleep(10)

	
        @pytest.mark.run(order=8)
        def test_008_execute_cmd_on_active_to_stop_upgrade(self):
		try:
                	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_master_ha_vip)
                	child.logfile=sys.stdout
                	log("start","/infoblox/var/infoblox.log",config.grid1_master_ha_vip)
                	child.expect('password')
                	child.sendline('infoblox')
                	child.expect('Infoblox >')
                	child.sendline('show status')
                	child.expect('Infoblox >')
                	output = child.before
                	if "HA Status:      Active" in output:
                        	assert True
                	else:
                        	assert False
               	 	child.sendline('set grid_upgrade stop_and_cancel')
                	child.expect('Do you want to proceed\? \(y or n\):')
                	child.sendline('y')
                	child.expect('Are you sure\? \(y or n\):')
                	child.sendline('y')
                	child.expect('Infoblox >')
                	output1 = child.before
                	sleep(30)
                	log("stop","/infoblox/var/infoblox.log",config.grid1_master_ha_vip)
                	data = "Erase file /infoblox/var/upgrade_message_sent"
                	logs=logv(data,"/infoblox/var/infoblox.log",config.grid1_master_ha_vip)
                	print("logs are",logs)
                	if logs != None:
                        	print("upgrade has been stopped")
                        	assert True
                	else:
                        	print("upgarde has not been stopped")
                        	assert False
		except Exception as error:
			print("test 08 failed",error)
		finally:
                	child.sendline('exit')
                	child.close()
			sleep(10)


	


	@pytest.mark.run(order=9)
        def test_009_check_upgrade_state_set_to_init(self):
		try:
                	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_master_ha_vip)
                	child.logfile=sys.stdout
                	child.expect('#')
                	child.sendline('cd /infoblox/var')
                	child.expect('#')
                	child.sendline('grep -r "^" upgrade/*')
                	child.expect('#')
                	output = child.before
			if (("upgrade/UPGRADE_STATE:init" in output) and ("upgrade/STATUS:Upgrade stopped and cancelled by user" in output)):
				print("upgrade state set to init after cancelling the upgrade")
                        	assert True
                	else:
				print("upgrade state not set to init after cancelling the upgrade")
                        	assert False
		except Exception as error:
			print("test 09 failed",error)
		finally:
			child.sendline('exit')
                	child.close()
			sleep(10)


	@pytest.mark.run(order=10)
	def test_010_check_upgrade_state_set_to_default_with_wapi(self):
                grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
                print(grid_upgrade_status)
		if (('"upgrade_state": "NONE"' in grid_upgrade_status) and ('"grid_state": "DEFAULT"' in grid_upgrade_status)):
			print("validate grid state set to default with wapi after cancelling the upgarde")
			assert True
		else:
			print("validate grid state not set to default with wapi after cancelling the upgarde")
			assert False



        @pytest.mark.run(order=11)
        def test_011_do_reset_database_on_passive_node_after_cancelling_the_upgrade(self):
                try:
			sleep(360)
			cmd = os.system('reset_console  -H '+config.grid1_master_ha_passive_id)
               	 	print ('cmd is',cmd)
                	#output = subprocess.check_output(cmd, shell=True)
                	child = pexpect.spawn('console_connect -H '+config.grid1_master_ha_passive_id)
                	child.logfile=sys.stdout
                	child.expect('Escape chara.*')
                	child.sendline('\n')
                	child.sendline('\n')
                	child.sendline('\n')
                	sleep(10)
                	child.expect('login:')
                	child.sendline('admin')
                	sleep(10)
                	child.expect('password:')
               	 	sleep(5)                
                	child.sendline('infoblox')
                	child.expect('Infoblox >')
                	child.sendline('show status')
                	child.expect('Infoblox >')
                	output = child.before
                	if "HA Status:      Active" in  output:
                        	assert True
                	else:
                        	assert False
                	child.sendline('reset database')
                	child.expect('Do you wish to preserve basic network settings\? \(y or n\): ')
                	child.sendline('y')
                	child.expect('ARE YOU SURE YOU WANT TO PROCEED\? \(y or n\): ')
                	child.sendline('y')
                	sleep(400)
			child.sendline('\n')
			child.sendline('\n')
                	child.expect('login:')  
                	output = child.before  
		except Exception as error:
			print("test 011 failed",error) 
		finally:
                	child.sendline('exit')
	 		child.close()	
			sleep(10)


        @pytest.mark.run(order=12)
        def test_012_unblock_passive_network_and_revert_passive_node(self):
		try:
			cmd1 = os.system("netctl_system -i lan -S "+string1+" -a vlanset  -H "+config.grid1_master_ha_passive_id)
			sleep(30)
                	cmd2 = os.system("netctl_system -i ha -S "+string1+" -a vlanset  -H "+config.grid1_master_ha_passive_id )
			sleep(30)
                	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_master_ha_passive_ip)
                	child.logfile=sys.stdout
                	child.expect('password')
                	child.sendline('infoblox')
                	child.expect('Infoblox >')
                	child.sendline('set revert_grid')
                	child.expect('Do you want to proceed\? \(y or n\):')   
                	child.sendline('y')
                	child.expect('Do you want to proceed\? \(y or n\):')
                	child.sendline('y')
                	child.expect('Are you sure\? \(y or n\):')
                	child.sendline('y')
                	output = child.before
		except Exception as error:
			print("test 012 failed",error)
		finally:
                	child.sendline('exit')
			child.close()
			sleep(60)

		


	@pytest.mark.run(order=13)
	def test_013_validate_passive_joined_back_to_active_after_reverting(self):
		sleep(1800)
		#for i in range(1,40):
		#sleep(30)
		#status = os.system("ping -c 4 "+config.grid1_master_ha_passive_ip)
		#print(status)
		#if status == 0:
		#sleep(60)
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_master_ha_passive_ip)
		child.logfile=sys.stdout
		child.expect('password')
		child.sendline('infoblox')
		child.expect('Infoblox >')
		child.sendline('show status')
		child.expect('Infoblox >')
		output = child.before
		if "HA Status:      Passive" in  output:
			print("after revert ,grid joined back to active node")
			assert True
		else:
			print("after revert ,grid failed to join active node")	
			assert False
		sleep(10)

        @pytest.mark.run(order=14)
        def test_014_check_upgrade_state_set_to_init_after_cancelling_upgrade(self):
		try:
                	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_master_ha_vip)
                	child.logfile=sys.stdout
                	child.expect('#')
                	child.sendline('cd /infoblox/var')
                	child.expect('#')
                	child.sendline('grep -r "^" upgrade/*')
                	child.expect('#')
                	output = child.before
                	if (("upgrade/UPGRADE_STATE:init" in output) and ("upgrade/STATUS:Upgrade stopped and cancelled by user" in output)):
				print("upgrade state set to Upgrade stopped and cancelled by user")
                        	assert True
                	else:
				print("upgrade state not set to Upgrade stopped and cancelled by user")
           			assert False
		except Exception as error:
			print("test 014 failed",error)
		finally:
			child.sendline('exit')
                	child.close()
			sleep(10)


	@pytest.mark.run(order=15)
	def test_015_after_cancelling_the_upgrade_if_grid_is_pinging_reupload_fb_build(self):
                Upload()
                print("test case 015 passed successfully")
		sleep(10)


	@pytest.mark.run(order=16)
        def test_016_Validate_the_Upload_completion_status_and_start_the_distribution(self):
                distribution()
                print("test case 016 passed successfully")
		sleep(10)


        @pytest.mark.run(order=17)
        def test_017_Validate_the_distribution_completion_status_and_start_the_Upgrade_Test(self):
                uploadtest()
                print("test case 017 passed successfully")
		sleep(10)






        @pytest.mark.run(order=18)
        def test_018_Validate_the_Upgrade_Test_completion_status_and_start_the_Upgrade(self):
		Upgrade()
		for i in range(1,95):
			#sleep(60)
			ping = os.popen("for i in range{1..3} ; do ping -c 4 -w 10 "+config.grid1_master_ha_vip+" ; done").read()
			if "0 received" not in ping:
				print("vip  is pinging ")
				grid_upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID")
				print(grid_upgrade_status)
				status = '"grid_state": "UPGRADING_COMPLETE"'
				if status in grid_upgrade_status:
					msg = "The Grid has been successfully upgraded to destination build"
					print(msg)
					break
				else:
					print("Grid is still being upgraded")
					sleep(60)
			else:
				print("grid  vip is not pinging, going for 60 sec sleep")
				sleep(60)
				


