def read_log(filename):
    with open(filename , "r") as file:
        logs = file.readlines()
    return logs

def extract_ip(log_line):
    parts = log_line.split()
    return parts[0]

# def extract_timestamp(log_line):
#     parts = log_line.split()
#     return parts[3]

# logs = read_log("sample.log")

# for log in logs:
    # ip = extract_ip(log)
    # timestamp = extract_timestamp(log)
    # print(ip)
    # print(timestamp)

def count_requests_by_ip(logs):
    ip_count = {}

    for log in logs:
        ip = extract_ip(log)

        if ip in ip_count:
            ip_count[ip] += 1
        else:
            ip_count[ip] = 1
    
    return ip_count

logs = read_log("sample.log")
ip_count = count_requests_by_ip(logs)

# print(ip_count)

def find_suspicious_ips(ip_count, threshold):
    suspicious = []

    for ip, count in ip_count.items():
        if count > threshold:
            suspicious.append((ip,count))

    return suspicious

suspicious_ips = find_suspicious_ips(ip_count, 3)

print("request count by IP:")
print(ip_count)

print("suspicious IPs: ")
print(suspicious_ips)
