def check_proposition(op):
    return op in list_of_operators


def segment(input):
    final = []
    loop_counter = 0
    length = len(input)
    while loop_counter < length:
        if check_proposition(input[loop_counter]):
            final.append(input[loop_counter])
            loop_counter += 1
        elif input[loop_counter] == " ":
            loop_counter += 1
        else:
            literal = ""
            while loop_counter < length and not check_proposition(input[loop_counter]) and input[loop_counter] != " ":
                literal += input[loop_counter]
                loop_counter += 1
            final.append(literal)
    return final


def slice_forward(input, id):
    temp = 0
    loop_counter = id
    while loop_counter < len(input):
        temp += 1 if input[loop_counter] == "(" else -1 if input[loop_counter] == ")" else 0
        if temp == 0 and input[loop_counter] != "!":
            return input[id : (loop_counter + 1)], loop_counter
        loop_counter += 1


def slice_back(input):
    temp = 0
    length = len(input)
    loop_counter = length - 1

    while loop_counter >= 0:
        temp += 1 if input[loop_counter] == ")" else -1 if input[loop_counter] == "(" else 0
        if temp == 0:
            loop_counter -= 1 if loop_counter > 0 and input[loop_counter - 1] == "!" else 0
            return input[loop_counter:length], input[0:loop_counter]
        loop_counter -= 1


def unary(input, operant):
    final = []
    loop_counter = 0
    while loop_counter < len(input):
        if input[loop_counter] == operant:
            loop_counter += 1
            slice, loop_counter = slice_forward(input, loop_counter)
            slice = unary(slice, operant)
            final += ["(", "!"] + slice.copy() + [")"]
        else:
            final.append(input[loop_counter])
        loop_counter += 1
    return final


def binary(input, operant):
    final = []
    loop_counter = 0
    while loop_counter < len(input):
        if input[loop_counter] == operant:
            temp, final = slice_back(final)
            temp = binary(temp, operant)
            loop_counter += 1
            slice, loop_counter = slice_forward(input, loop_counter)
            slice = binary(slice, operant)
            final += (["("] + temp.copy() + [operant] + slice.copy() + [")"])
        else:
            final.append(input[loop_counter])
        loop_counter += 1
    return final


def brackets(input):
    input = unary(input, "!")
    input = binary(input, "&")
    input = binary(input, "|")
    input = binary(input, ">")
    input = binary(input, "=")
    return input


def literal_not_protected(input):
    if not any(check_proposition(loop_counter) for loop_counter in input):
        return False
    temp = 0
    for loop_counter in range(0, len(input)):
        if input[loop_counter] == "(":
            temp += 1
        elif input[loop_counter] == ")":
            temp -= 1
        elif temp == 0:
            return True
    return False


def equivalent_iff(input1, input2):
    return (["(", "("]+ input1.copy()+ [">"]+ input2.copy()+ [")", "&", "("]+ input2.copy()+ [">"]+ input1.copy()+ [")", ")"])


def equivalent_implies(input1, input2):
    return ["(", "(", "!"] + input1.copy() + [")", "|"] + input2.copy() + [")"]


def remove_operant(input, operant):
    final = []
    loop_counter = 0
    while loop_counter < len(input):
        if input[loop_counter] == operant:
            temp, final = slice_back(final)
            loop_counter += 1
            temp2, loop_counter = slice_forward(input, loop_counter)
            temp = remove_operant(temp, operant)
            temp2 = remove_operant(temp2, operant)
            final += (equivalent_iff(temp, temp2) if operant == "=" else equivalent_implies(temp, temp2)).copy()
        else:
            final.append(input[loop_counter])
        loop_counter += 1
    return final


def move_not_inwards(input):
    final = []
    while True:
        final = []
        loop_counter = 0
        while loop_counter < len(input):
            if input[loop_counter] == "!":
                loop_counter += 1
                temp, loop_counter = slice_forward(input, loop_counter)
                if temp[0] == "(":
                    final.append("(")
                    loop_counter2 = 1
                    while loop_counter2 < len(temp):
                        tmp, loop_counter2 = slice_forward(temp, loop_counter2)
                        tmp.pop(0) if tmp[0] == "!" else tmp.insert(0, "!")
                        final += tmp.copy()
                        loop_counter2 += 1
                        if loop_counter2 < len(temp) - 1:
                            final += (["&"] if temp[loop_counter2] == "|" else ["|"] if (temp[loop_counter2] == "&") else [])
                        loop_counter2 += 1
                    final.append(")")
                else:
                    temp.pop(0) if temp[0] == "!" else final.append("!")
                    final += temp.copy()
            else:
                final.append(input[loop_counter])
            loop_counter += 1
        if final == input:
            break
        input = final
    return final


def or_over_and(input):
    final = []
    loop_counter = 0
    while loop_counter < len(input):
        if input[loop_counter] == "|":
            temp, final = slice_back(final)
            temp = or_over_and(temp)
            tmp3 = []
            if temp[0] == "(":
                loop_counter2 = 1
                while loop_counter2 < (len(temp) - 1):
                    tmp, loop_counter2 = slice_forward(temp, loop_counter2)
                    tmp3.append(tmp.copy())
                    loop_counter2 += 2
            else:
                tmp3.append(temp.copy())
            loop_counter += 1
            assert loop_counter < len(input)
            temp2, loop_counter = slice_forward(input, loop_counter)
            temp2 = or_over_and(temp2)
            tmp2 = []
            if temp2[0] == "(":
                loop_counter2 = 1
                while loop_counter2 < (len(temp2) - 1):
                    tmp, loop_counter2 = slice_forward(temp2, loop_counter2)
                    tmp2.append(tmp.copy())
                    loop_counter2 += 2
            else:
                tmp2.append(temp2.copy())
            for k in range(0, len(tmp2)):
                for m in range(0, len(tmp3)):
                    final += (["("]+ tmp3[m].copy()+ ["|"] + tmp2[k].copy()+ [")"]+ (["&"] if m != len(tmp3) - 1 else []))
                final += ["&"] if k != len(tmp2) - 1 else []
        else:
            final.append(input[loop_counter])
        loop_counter += 1
    return final


def remove_parenthesis(input):
    final = []
    brackets = []
    content = []
    for loop_counter in range(0, len(input)):
        if input[loop_counter] == "(":
            content.append(final.copy())
            brackets.append("(")
            final.clear()
        elif input[loop_counter] == ")" and len(content):
            if literal_not_protected(final):
                final = ["("] + final + [")"]
            final = content[len(content) - 1].copy() + final
            brackets.pop()
            content.pop()
        else:
            final.append(input[loop_counter])
    return final


def process_operant(input):
    input = remove_parenthesis(input)
    if input[0] == "(":
        return (["("]+ [loop_counter for loop_counter in input[1 : len(input) - 1] if loop_counter not in ["(", ")"]]+ [")"])
    else:
        return [loop_counter for loop_counter in input[0 : len(input)] if loop_counter not in ["(", ")"]]


def split_and(input):
    final = []
    temp = []
    for i in range(0, len(input)):
        if input[i] == "&":
            final += process_operant(temp).copy()
            final.append("&")
            temp.clear()
        else:
            temp.append(input[i])
    return final + process_operant(temp).copy()


def cnf(input):
    input = remove_operant(input, "=")
    input = remove_parenthesis(input)
    input = remove_operant(input, ">")
    input = remove_parenthesis(input)
    input = move_not_inwards(input)
    input = remove_parenthesis(input)
    temp = []
    while temp != input:
        temp = input
        input = or_over_and(input)
        input = remove_parenthesis(input)
    return split_and(input)


def clause(input):
    final = {}
    loop_counter = 1 if input[0] == "(" else 0
    length = len(input) - 1 if input[0] == "(" else len(input)
    while loop_counter < length:
        literal, loop_counter = slice_forward(input, loop_counter)
        if literal[0] == "!":
            final[literal[1]] = True
        else:
            final[literal[0]] = False
        loop_counter += 2
    return final


def dict_change(input):
    return ", ".join([("!" if input[key] else "") + str(key) for key in input])


def resolve_function(input, shall_print):
    clause = []
    clauses = []
    clause_maps = []
    for literal in input:
        if literal == "&":
            clauses.append("".join(clause))
            clause_maps.append(clause_map(clause))
            clause.clear()
        else:
            clause.append(literal)
    clauses.append("".join(clause))
    clause_maps.append(clause_map(clause))
    new_clause_maps = []
    if shall_print:
        print("Clauses: {}".format(clauses))
    while True:
        for loop_counter in range(0, len(clause_maps)):
            for loop_counter2 in range((loop_counter + 1), len(clause_maps)):
                res = {}
                for temp in clause_maps[loop_counter]:
                    if (temp not in clause_maps[loop_counter2]or clause_maps[loop_counter2][temp] == clause_maps[loop_counter][temp]):
                        res[temp] = clause_maps[loop_counter][temp]
                for temp in clause_maps[loop_counter2]:
                    if temp not in clause_maps[loop_counter]:
                        res[temp] = clause_maps[loop_counter2][temp]
                    print(
                    "({}) <- RESOLVE(({}), ({}))".format(format_dict(res),format_dict(clause_maps[loop_counter]),format_dict(clause_maps[loop_counter2]),
                    )
                ) if shall_print else None
                if not bool(res):
                    print(
                        "If Resolvents contains the empty clause: Return True."
                    ) if shall_print else None
                    return True
                new_clause_maps.append(
                    res
                ) if res not in new_clause_maps else None
                print("New Clauses <- New Clauses ∪ Resolvents") if shall_print else None
        if all(new_clause_map in clause_maps for new_clause_map in new_clause_maps):
            print("If New Clauses ⊆ Clauses : Return False") if shall_print else None
            return False
        clause_maps += [
            new_clause_map
            for new_clause_map in new_clause_maps
            if new_clause_map not in clause_maps
        ]
        print("Clauses <- Clauses ∪ New Clauses") if shall_print else None


def vet_sen(input):
    input = brackets(input)
    input = remove_parenthesis(input)
    return cnf(input)


def fetch_input(input):
    number_prop_sent = input[0].split(" ")[0]
    number_prop_sent = int(number_prop_sent)
    query_index=number_prop_sent+1
    shall_print=1
    final = []
    while number_prop_sent:
        final.append(input[number_prop_sent])
        number_prop_sent -= 1
    to_prove = input[query_index].split("\n")
    return shall_print, final, to_prove


def main():
    path = input("Enter the file name: ")
    f = open(path)
    file_content = f.readlines()
    f.close()
    shall_print, sentences, to_prove = fetch_input(file_content)
    kb = []
    for sentence in sentences:
        print('sentence',sentence)
        sentence = vet_sen(segment(sentence))
        kb += sentence.copy()
        kb.append("&")
    kb.pop()
    to_prove = vet_sen(segment(to_prove))
    print('to_prove: ',to_prove)
    ip_resolution = ["!"] + to_prove.copy()
    if len(kb) > 0:
        ip_resolution = kb.copy() + ["&", "("] + ip_resolution.copy() + [")"]
    if len(ip_resolution):
        ip_resolution = vet_sen(ip_resolution)
        return int(resolve_function(ip_resolution, shall_print))

list_of_operators = ["!", "&", "|", ">", "=", "(", ")"]
