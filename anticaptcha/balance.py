from anticaptchaofficial.recaptchav2proxyless import *

solver = recaptchaV2Proxyless() # or any other class
solver.set_verbose(1)
solver.set_key("YOUR-API-KEY")
money_balance = solver.get_balance()
print (money_balance)
subscription_credits_balance = solver.get_credits_balance()
print(subscription_credits_balance)