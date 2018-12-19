import random
import copy
import json
from smsgateway import SMSGateway, Message


class Person:
    def __init__(self, id, name, phone):
        self.id = id
        self.name = name
        self.phone = phone
        self.secret_santa = None

    def __str__(self):
        if self.secret_santa is None:
            return 'id: {}, name : {}, phone: {}'.format(self.id, self.name, self.phone)
        return 'id: {}, name : {}, phone: {}\n\tsecret santa: {}'.format(self.id, self.name, self.phone, self.secret_santa)

    def __eq__(self, other):
        return self.id == other


class Family:
    def __init__(self, family_path):
        self.members = []
        self.path = family_path
        self.load_family()

    def load_family(self):
        with open(self.path, 'r') as f:
            lines = [n.split('-') for n in f.readlines()]
            line_counter = 0
            for line in lines:
                if len(line) == 1 and line[0] is '\n':
                    continue
                elif len(line) != 2:
                    raise Exception('{} should have only 2 values. Check your family file.'.format(data))
                self.members.append(Person(line_counter, line[0].strip(), line[1].strip()))
                line_counter +=1

    def asign_secret_santas(self):
        copy_members = copy.deepcopy(self.members)
        used_idx = []
        for i in range(len(self.members)):
            random_santa_idx = random.randint(0, len(copy_members)-1)
            # Check we already not used this idx
            while random_santa_idx in used_idx:
                random_santa_idx = random.randint(0, len(copy_members)-1)
            # Check it is not himself
            while self.members[i] == copy_members[random_santa_idx]:
                random_santa_idx = random.randint(0, len(copy_members)-1)
            used_idx.append(random_santa_idx)
            self.members[i].secret_santa = copy_members[random_santa_idx]

    def send_all_sms(self, client=None):
        for member in self.members:
            message = self.send_sms(member)
            status = client.send_sms(message)

    def send_sms(self, member):
        mensaje = 'Hola {},\nLa navidad ha llegado y con ello el familiar invisible.\nSi eres quien digo ser, ' \
                  'tu amigo invisible es {}.\nBesis!'.format(member.name, member.secret_santa.name)

        return Message(member.phone, mensaje, 107036)


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    print(config)
    random.seed(config['seed'])
    input_family = config['family_name']
    client = SMSGateway(config['api_token'])

    fabian_family = Family(input_family)
    fabian_family.asign_secret_santas()
    fabian_family.send_all_sms(client)
