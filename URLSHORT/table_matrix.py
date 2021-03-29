def build_links_matrix(query_results, sql_data):
    data = sql_data
    header_matrix = ['Shortened Url','Long Url', 'Date Created']
    row_matrix = []
    for x in range(0,query_results):
        row = []
        row.append("https://sh-ur.com/l/"+data[x]['url_shortened'])
        row.append(data[x]['url_long'])
        row.append(f"{data[x]['url_timecreated']}")
        row_matrix.append(row)
        x+=1

    return [header_matrix, row_matrix]