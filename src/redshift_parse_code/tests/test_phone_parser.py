import unittest
import sys
import os
import json


from context import PhoneParser
from io import BytesIO

class PhoneParserTestCases(unittest.TestCase):
    area_code_event_json = '2018-04-20T19:45:24.349Z idp {"id":"b17wpieoqf35-525a-44oeodb-c904d4ac0b1e","name":"OTP: Delivery Selection","properties":{"event_properties":{"success":true,"errors":{},"otp_delivery_preference":"sms","resend":null,"country_code":"1","area_code":"805","context":"confirmation"},"user_id":"06a2f306-0f89-4f53-ab20-ddf1a3e9edde","user_ip":"204.14.239.105","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36","host":"secure.login.gov","pid":18484},"visit_id":"7e05fd69-69bf-4d5e-882c-873488ac4f9a","visitor_id":"0a2d3b0a-c866-46ff-a6af-174455135a8a","time":"2017-10-22T19:44:13.775Z"}'
    
    test_event_log_txt = BytesIO(b"""
    2018-04-20T19:45:24.349Z idp-.login.gov [20/Apr/2018:19:45:15 +0000] secure.login.gov:443 : 00.000.000.47 - (172.16.33.247) - "HEAD /13746/ HTTP/1.1" 404 "Not Found" 0 Bytes "-" "DirBuster-0.12 (http://www.owasp.org/index.php/Category:OWASP_DirBuster_Project)" 0.035 sec "Root=b17wpieoqf35-525a-44oeodb-bdi512-c904d4ac0b1e"
    2018-04-20T19:45:24.349Z idp-prod.login.gov {"id":"b176d1e","name":"OTP: Delivery Selection","properties":{"event_properties":{"success":true,"errors":{},"otp_delivery_preference":"sms","resend":null,"country_code":"1","area_code":"805","context":"confirmation"},"user_id":"06a2f306-0f89-4f53-ab20-ddf1a3e9edde","user_ip":"204.14.239.105","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36","host":"secure.login.gov","pid":18484},"visit_id":"7e05fd69","visitor_id":"0a2d3b0a","time":"2017-10-22T19:44:13.775Z"}
    """)

    in_io = test_event_log_txt.read()

    def test_extract_json(self):
      parser = PhoneParser()
      data = parser.extract_json(self.area_code_event_json, line_num=1)
      self.assertEqual(data['id'], 'b17wpieoqf35-525a-44oeodb-c904d4ac0b1e')
      self.assertEqual(data['visit_id'], '7e05fd69-69bf-4d5e-882c-873488ac4f9a')
      self.assertEqual(data['visitor_id'],'0a2d3b0a-c866-46ff-a6af-174455135a8a')
      self.assertEqual(data['properties']['event_properties']['area_code'], '805')
      self.assertEqual(data['properties']['event_properties']['country_code'], '1')

    def test_json_to_csv(self):
      parser = PhoneParser()
      data = parser.extract_json(self.area_code_event_json, line_num=1)
      res = parser.json_to_csv(data)[0]
      self.assertEqual(len(res), 6)
      self.assertEqual(res[5], '2017-10-22 19:44:13')
    
    def test_has_valid_json(self):
      parser = PhoneParser()
      self.assertTrue(parser.has_valid_json(self.area_code_event_json, line_num=1))

if __name__ == '__main__':
   unittest.main()
