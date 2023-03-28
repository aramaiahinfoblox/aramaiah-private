import re
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import json
import time
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import pexpect
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="SPTYRFE_52.log" ,level=logging.INFO,filemode='w')

def print_and_log(arg=""):
	print(arg)
	logging.info(arg)

def upload_ca_cert(file_name):
    create_file = ib_NIOS.wapi_request('POST', object_type="fileop", params="?_function=uploadinit")
    print_and_log(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    print_and_log(token)
    url = json.loads(create_file)['url']
    print_and_log(url)
    os.system("curl -k -u admin:infoblox -H 'content-typemultipart-formdata' '" + url + "' -F file=@"+file_name)
    data = {"token": token, "certificate_usage": "EAP_CA"}
    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data), params="?_function=uploadcertificate")
    print_and_log(response)
    return response

def delete_ca_cert():
    response = ib_NIOS.wapi_request('GET', object_type="cacertificate")
    response = json.loads(response)
    ref = response[0]['_ref']
    delete = ib_NIOS.wapi_request('DELETE', object_type=ref)
    return delete

def run_cli_command_show_verify_certificates(result):
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid_vip)
        child.logfile = sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show  verify_certificates')
        child.expect('Infoblox >')
        response = child.before
        print_and_log(response)
        assert re.search(result, response)
    except Exception as e:
        print_and_log("Error while executing the CLI command")
        print_and_log(e)
        assert False
    finally:
        child.close()

def get_grid_ref():
    response = ib_NIOS.wapi_request('GET', object_type="grid")
    response = json.loads(response)
    ref = response[0]['_ref']
    print_and_log(ref)
    return ref

def check_the_ping_status():
    for i in range(300):
        output = os.system("ping -c 2 " + config.grid_vip)
        if output == 0:
            print_and_log("Grid master is reachable")
            break
        else:
            print_and_log("Ping failed, checking Ping again")
            sleep(1)
            continue


class SPTYRFE_52(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Adding_CA_certificate(self):
        print_and_log("************ Adding CA certificate ************")
        output = upload_ca_cert("ca.pem")
        if output != "{}":
            print_and_log("Certificate Upload failed")
            assert False
        else:
            print_and_log("Certificate upload Passed")
            assert True
        sleep(60)
        print_and_log("************ Test Case 1 Execution Completed ************")

    @pytest.mark.run(order=2)
    def test_002_Validating_CA_certificate(self):
        print_and_log("************ Validating CA certificate ************")
        grid_ref = get_grid_ref()
        response = ib_NIOS.wapi_request('POST', object_type=grid_ref, params="?_function=validatecertificates")
        response = json.loads(response)
        output = response['complete_verification_result']
        print_and_log(output)
        result = []
        for i in output:
            result.append(i['verify_result'])
        print_and_log(result)
        match = "\Winfoblox\Wsecurity\Wcerts\Waaa_ca_cert.pem\W\sOK\s"
        flag = False
        for i in result:
            new = re.search(match, i)
            if new:
                flag = True
                print_and_log(i)
            else:
                continue
        if flag != True:
            print_and_log("Error in validating the CA cert")
            assert False
        else:
            print_and_log("CA Cert Validation is successfull")
            assert True
        print_and_log("************ Test Case 2 Execution Completed ************")


    @pytest.mark.run(order=3)
    def test_003_Validating_Verify_certificates_command(self):
        print_and_log("************ Validating Verify certificates command ************")
        output = run_cli_command_show_verify_certificates('aaa_ca_cert.pem: OK')
        print_and_log("************ Test Case 3 Execution Completed ************")


    @pytest.mark.run(order=4)
    def test_004_Adding_DTC_Https_health_monitor_certificate(self):
        print_and_log("************ Adding DTC Https health monitor certificate ************")
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop", params="?_function=uploadinit")
        print_and_log(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        print_and_log(token)
        url = json.loads(create_file)['url']
        print_and_log(url)
        os.system("curl -k -u admin:infoblox -H 'content-typemultipart-formdata' '" + url + "' -F file=@combined_dtc_https.pem")
        data = {"token": token}
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=add_certificate")
        print_and_log(response)
        sleep(60)
        if response != "{}":
            print_and_log("Certificate Upload failed")
            assert False
        else:
            print_and_log("Certificate upload Passed")
            assert True
        print_and_log("************ Test Case 4 Execution Completed ************")

    @pytest.mark.run(order=5)
    def test_005_Validating_dtc_https_certificate(self):
        print_and_log("************ Validating dtc https certificate ************")
        grid_ref = get_grid_ref()
        response = ib_NIOS.wapi_request('POST', object_type=grid_ref, params="?_function=validatecertificates")
        response = json.loads(response)
        output = response['complete_verification_result']
        print_and_log(output)
        result = []
        for i in output:
            result.append(i['verify_result'])
        print_and_log(result)
        match = "\Wstorage\Wtmp\Wcert1.pem\W\sOK\s"
        flag = False
        for i in result:
            new = re.search(match, i)
            if new:
                flag = True
                print_and_log(i)
            else:
                continue
        if flag != True:
            print_and_log("Error in validating the CA cert")
            assert False
        else:
            print_and_log("CA Cert Validation is successfull")
            assert True
        print_and_log("************ Test Case 5 Execution Completed ************")


    @pytest.mark.run(order=6)
    def test_006_Validating_DTC_Https_health_monitor_certificate_in_CLI(self):
        print_and_log("************ Validating DTC Https health monitor certificate in CLI ************")
        output = run_cli_command_show_verify_certificates('/tmp/cert1.pem: OK')
        #assert re.search(r'/storage/tmp/cert0.pem: OK', response)
        print_and_log("************ Test Case 6 Execution Completed ************")


    @pytest.mark.run(order=7)
    def test_007_Delete_the_valid_CA_certificate(self):
        print_and_log("************ Delete the valid CA certificate ************")
        check_the_ping_status()
        output = delete_ca_cert()
        print_and_log(output)
        assert re.search(r'cacertificate', output)
        sleep(60)
        print_and_log("************ Test case 7 Execution completed ************")

    @pytest.mark.run(order=8)
    def test_008_Adding_Expired_certificate(self):
        print_and_log("************ Adding Expired certificate ************")
        check_the_ping_status()
        output = upload_ca_cert("expired.pem")
        if output != "{}":
            print_and_log("Certificate Upload failed")
            assert False
        else:
            print_and_log("Certificate upload Passed")
            assert True
        sleep(60)
        print_and_log("************ Test Case 8 Execution Completed ************")


    @pytest.mark.run(order=9)
    def test_009_Validating_expired_CA_certificate(self):
        print_and_log("************ Validating expired CA certificate ************")
        grid_ref = get_grid_ref()
        response = ib_NIOS.wapi_request('POST', object_type=grid_ref, params="?_function=validatecertificates")
        response = json.loads(response)
        output = response['complete_verification_result']
        print_and_log(output)
        result = []
        for i in output:
            result.append(i['verify_result'])
        print_and_log(result)
        match = ".*certificate\shas\sexpired\sOK\s"
        flag = False
        for i in result:
            new = re.search(match, i)
            if new:
                flag = True
                print_and_log(i)
            else:
                continue
        if flag != True:
            print_and_log("Error in validating the CA cert")
            assert False
        else:
            print_and_log("CA Cert Validation is successfull")
            assert True
        print_and_log("************ Test Case 9 Execution Completed ************")

    @pytest.mark.run(order=10)
    def test_010_Validating_Expired_certificate_in_CLI(self):
        print_and_log("************ Validating Expired certificate in CLI ************")
        output = run_cli_command_show_verify_certificates('certificate has expired')
        #assert re.search(r'certificate has expired', response)
        print_and_log("************ Test Case 10 Execution Completed ************")

    @pytest.mark.run(order=11)
    def test_011_Delete_the_expired_CA_certificate(self):
        print_and_log("************ Delete the expired CA certificate ************")
        check_the_ping_status()
        output = delete_ca_cert()
        print_and_log(output)
        assert re.search(r'cacertificate', output)
        sleep(60)
        print_and_log("************ Test case 11 Execution completed ************")

    @pytest.mark.run(order=12)
    def test_012_Adding_Invalid_certificate(self):
        print_and_log("************ Adding Invalid certificate ************")
        check_the_ping_status()
        output = upload_ca_cert("invalid.pem")
        if output != "{}":
            print_and_log("Certificate Upload failed")
            assert False
        else:
            print_and_log("Certificate upload Passed")
            assert True
        sleep(90)
        print_and_log("************ Test Case 12 Execution Completed ************")

    @pytest.mark.run(order=13)
    def test_013_Validating_invalid_certificate(self):
        print_and_log("************ Validating expired CA certificate ************")
        grid_ref = get_grid_ref()
        response = ib_NIOS.wapi_request('POST', object_type=grid_ref, params="?_function=validatecertificates")
        response = json.loads(response)
        output = response['complete_verification_result']
        print_and_log(output)
        result = []
        for i in output:
            result.append(i['verify_result'])
        print_and_log(result)
        match = ".*Warning.\scontains\sCA\scertificate.s.\swithout\sSKI"
        flag = False
        for i in result:
            new = re.search(match, i)
            if new:
                flag = True
                print_and_log(i)
            else:
                continue
        if flag != True:
            print_and_log("Error in validating the Invalid CA cert")
            assert False
        else:
            print_and_log("CA Cert Validation is successfull for Invalid cert")
            assert True
        print_and_log("************ Test Case 13 Execution Completed ************")

    @pytest.mark.run(order=14)
    def test_014_Validating_invalid_certificate_in_CLI(self):
        print_and_log("************ Validating invalid certificate in CLI ************")
        output = run_cli_command_show_verify_certificates('.*Warning.\scontains\sCA\scertificate.s.\swithout\sSKI')
        print_and_log("************ Test Case 14 Execution Completed ************")

    @pytest.mark.run(order=15)
    def test_015_Delete_the_Inavlid_CA_certificate(self):
        print_and_log("************ Delete the Invalid CA certificate *************")
        check_the_ping_status()
        output = delete_ca_cert()
        print_and_log(output)
        assert re.search(r'cacertificate', output)
        sleep(90)
        print_and_log("************ Test case 15 Execution completed ************")\

    '''    
    @pytest.mark.run(order=16)
    def test_016_Upload_different_services_CA_cert(self):
        print_and_log("************ Upload different services CA cert ****************")
        for root, dirs, files in os.walk('./certs'):
            for file in files:
                print_and_log(file)
                upload_ca_cert(file)
                sleep(30)
        print_and_log("************ Test case 16 Execution completed ************")

    @pytest.mark.run(order=17)
    def test_017_Validation_of_status_of_all_the_ca_certs_uploaded_in_the_grid(self):
        pass
    '''

