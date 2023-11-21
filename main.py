#pip install dnspython

import re
import dns.resolver
import pandas as pd

url_string = str(input("Enter URL to CSV File: "))

data = pd.read_csv(url_string)

disposable_email_domains = ['mailinator.com', 'tempmail.com', '10minutemail.com']

def domain_exists(email):
    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception as e:
        print("Error", end="")
        return False

def is_valid_email(email):
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return pattern.match(email)

def is_not_disposable_email(email):
    domain = email.split('@')[-1]
    return not domain in disposable_email_domains

def is_not_role_based_email(email):
    role_based_keywords = ['info', 'support', 'sales', 'admin', 'contact']
    local_part = email.split('@')[0]
    return not any(keyword in local_part for keyword in role_based_keywords)

def is_mostly_numeric(email):
    return bool(re.match(r"^\d+[\d\w]*@\w+\.\w+$", email))

def has_sequential_chars(email):
    return re.search(r"(.)\1{3,}", email) is not None

def verify_email(row, current_index, total_count):
  email = row['email']
  valid = True
  if not is_valid_email(email):
      valid = False
  if not is_not_disposable_email(email):
      valid = False
  if not is_not_role_based_email(email):
      valid = False
  if is_mostly_numeric(email):
      valid = False
  if has_sequential_chars(email):
      valid = False
  if not domain_exists(email):
      valid = False
  
  if valid:
    print(f"\r. {current_index+1} of {total_count}", end="")
  else:
    print(f"\rR {current_index+1} of {total_count}", end="")
    
  return valid

def clean(data):
  total_count = len(data)
  truthy_data = [verify_email(row, idx, total_count) for idx, row in data.iterrows()]
  cleaned_list = data[truthy_data]

  difference = len(data) - len(cleaned_list)
  return cleaned_list, f"{difference} emails have been removed from the list"


data, stats = clean(data)
print(f"\n{stats}")

export_name = str(input("Please enter a filename to save the cleaned email list (e.g., 'cleaned_emails.csv'):")) + ".csv"

data.to_csv(export_name, index=False)
