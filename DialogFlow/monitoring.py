def initiate_logFile():
    import csv
    fieldnames = ['ConversationID', 'UserInput', 'PredictedIntents', 'ChatBotReply', 'Enteties']
    with open('logfile.csv', mode='a') as csv_file:
        audit_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        audit_writer.writeheader()
    return 

def add_logFile(ConversationID,UserInput,PredictedIntents,ChatBotReply,Enteties):
    import csv
    fieldnames = ['ConversationID', 'UserInput', 'PredictedIntents', 'ChatBotReply', 'Enteties']
    with open(r'logfile.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'ConversationID': ConversationID, 
            'UserInput': UserInput,
            'PredictedIntents':PredictedIntents, 
            'ChatBotReply': ChatBotReply,
            'Enteties':Enteties})

def generate_ConversationID():
    import uuid
    return uuid.uuid4()