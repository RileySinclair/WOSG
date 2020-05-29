from wos import split_lists


class DummyMember:
    def __init__(self, name):
        self.display_name = name


list1 = ["0000" + str(each) for each in range(1, 10)]
list2 = ["00" + str(each) for each in range(10, 100)]
list3 = ["0" + str(each) for each in range(100, 1000)]
list4 = ["1000", "1001", "1002"]
list_of_digits = list1 + list2 + list3 + list4

dummy_member = DummyMember("Username")

# list_of_participants = ["Username" + list_of_digits[each] for each in range(0, 101)]
# print(len(str([y for y in list_of_participants])))
# print(len(list_of_participants))
# #print(list_of_participants)
#
# list_of_lists = split_lists(list_of_participants, 400)
#
# for each in list_of_lists:
#     print(len(str([y for y in each])))
#     print(str([y for y in each]))


