def generate_relation_code(n_relations):
    for i in range(1, n_relations+1):
        print(f"ON BATCH UPDATE OF R{i} {{")
        print(f"  TMP_R{i}(long)[][A{i}, A{i+1}]<Local> := (DELTA R{i})(A{i}, A{i+1});")
        print(f"  V_R{i}(long)[][A{i}, A{i+1}]<Local> += TMP_R{i}(long)[][A{i}, A{i+1}]<Local>;")
        print(f"  V_Q(long)[][]<Local> += AggSum([],")
        v_expressions = [f"V_R{j}(A{j}, A{j+1})" for j in range(1, n_relations+1)]
        v_expressions[i-1] = f"TMP_R{i}(long)[][A{i}, A{i+1}]"
        print(f"    { ' * '.join(v_expressions) } * A1 * A{n_relations+1}")
        print("  );")
        print("}")

# Call the function with the number of relations you want to generate code for:
generate_relation_code(20)


