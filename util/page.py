def getPage(data, page, limit):
    limit = int(limit)
    page = int(page)

    length = len(data)
    page_num = length // limit + 1

    if page_num == 1:
        return data
    else:
        start_num = limit * (page - 1)
        end_num = start_num + limit
        if length<=end_num:
            end_num=length
        res_data = []
        for i in range(start_num, end_num):
            if data[i] is None:
                break
            res_data.append(data[i])
        return res_data
