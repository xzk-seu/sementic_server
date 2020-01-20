import json


def print_data(data):
    err = [x for x in data if x["res_sentence"] == "不通过"]
    print("不通过:", len(err), len(data), len(err) / len(data))
    err = [x for x in data if x["status"] == "202"]
    print("202:", len(err), len(data), len(err) / len(data))
    err = [x for x in data if x["status"] == "400"]
    print("400:", len(err), len(data), len(err) / len(data))
    err = [x for x in data if x["status"] == "200"]
    print("200:", len(err), len(data), len(err) / len(data))
    err = [x for x in data if x["status"] != "200"]
    print("not 200:", len(err), len(data), len(err) / len(data))
    print()


def main():
    with open("test_result_0111.json", "r") as fr:
        data = json.load(fr)
    data = [x for x in data if x["status"] == "200"]
    result = dict()
    for i in data:
        rel_loss = i.get("rel_loss")
        rel_loss = json.loads(rel_loss.replace("'", "\""))
        if rel_loss and len(rel_loss) > 0:
            print(i['sentence'], rel_loss)
            for rel in rel_loss:
                link_type = rel['link_type']
                temp = result.setdefault(link_type, list())
                temp.append(i['sentence'])

    for k, v in result.items():
        print(k, ":")
        for s in v:
            print("\t", s)

    print_data(data)


if __name__ == '__main__':
    main()
