# -*- coding: utf-8 -*-
import math

def count_one(minterm_string):
    n_variable=len(minterm_string)
    n_one=0
    for i in range(n_variable):
        if minterm_string[i]=='1':
            n_one+=1
    return n_one

def decode(minterm,n_variables):
    """
    输入最小项编号，输出最小项的01串
    :param minterm: 待转化成string的
    :param n_variables: 变元数量
    :return: 最小项的01串
    :rtype: str
    """
    result=['0']*n_variables
    for i in reversed(range(n_variables)):
        result[i]=str(minterm%2)
        minterm=minterm//2
    return ''.join(result)

def find_common(minterm_string_a,minterm_string_b):
    """
    如果两个字符串对应蕴含项仅有一位不同，输出下一列的蕴含项字符串；否则输出None
    -表示已经消去变量，二者的-必须在相同变元上
    """
    n_variables=len(minterm_string_a)
    n_difference=0
    result=['a']*n_variables
    for i in range(n_variables):
        if minterm_string_a[i]=='-' or minterm_string_b[i]=='-':
            if minterm_string_a[i]!=minterm_string_b[i]:
                return None
            else:
                result[i]='-'
                continue
        elif minterm_string_a[i]==minterm_string_b[i]:
            result[i]=minterm_string_a[i]
        else:
            result[i]='-'
            n_difference+=1
        if n_difference>=2:#corner case:只有两个变元的时候，会不会返回空或者返回错误字符串
            return None
    return ''.join(result)

def  get_implicant_table(minterms,dcs,n_variables):
    """
    得到蕴含项表prime_implicant_table
    implicant_table[i][j]是一个存储第i+1列含j个1的蕴含项的字典，键值对str:(minterms,isnotprime),键是蕴含项字符串，值的第一项是蕴含最小项编号，第二项是否本原
    :param minterms:
    :param dcs:
    :param n_variables:
    :return: list<list<dict<str:(set,bool)>>>
    """

    n_loop = int(math.floor(math.log(len(minterms), 2)))
    implicant_table = [[{} for i in range(n_variables + 1)] for j in range(n_loop + 1)]

    # 解码字符串
    for minterm in minterms + dcs:
        str1 = decode(minterm, n_variables)
        n_one = count_one(str1)  #
        implicant_table[0][n_one][str1] = (set([minterm]), False)

    # 生成第i+2列的蕴含表，再判断第i列哪些是本原项
    for i in range(n_loop):
        # 生成蕴含表
        for j in range(n_variables):
            for str1, (minterms1, is_not_prime1) in implicant_table[i][j].items():
                for str2, (minterms2, is_not_prime2) in implicant_table[i][j + 1].items():
                    tmp = find_common(str1, str2)
                    if tmp != None:
                        implicant_table[i + 1][j][tmp] = (minterms1.union(minterms2), False)
        # 判断非本原项
        for j in range(n_variables):
            for str2, (minterms2, is_not_prime2) in implicant_table[i + 1][j].items():
                # 对后一列有贡献的项（因而不是本原）的1的个数与前者相等或者多1
                for str1, (minterms1, is_not_prime1) in implicant_table[i][j].items():
                    if is_not_prime1:
                        continue
                    if minterms1.intersection(minterms2) == minterms1:
                        # 不是本原项
                        implicant_table[i][j][str1] = (minterms1, True)
                for str1, (minterms1, is_not_prime1) in implicant_table[i][j + 1].items():
                    if is_not_prime1:
                        continue
                    if minterms1.intersection(minterms2) == minterms1:
                        # 不是本原项
                        implicant_table[i][j + 1][str1] = (minterms1, True)
    return implicant_table

def get_coverable_implicant(implicant_set, minitem, prime_implicant_dict):
    """
    从集合中选出可覆盖给定最小项的蕴含项
    :param prime_implicant_dict: 全部本源蕴含项的字典，键字符串，值是覆盖的最小项
    :type prime_implicant_dict: dict<str:set<int>>
    :return:覆盖给定最小项的蕴含项集合
    :rtype:set<str>
    """
    result =set()
    for implicant in implicant_set:
        if minitem in prime_implicant_dict[implicant]:
            result.add(implicant)
    return result


def get_prime_implicant_dict(implicant_table):
    """
    得到本质蕴含项字典
    :param implicant_table: 蕴含项表
    :type implicant_table:list<list<dict<str:(set,bool)>>>
    :return: 本质蕴含项字典str:set，其中str为字符表示,set为覆盖的最小项集合，
    :rtype: dict<str:set<int>>
    """
    prime_implicant_dict={}
    for i in range(len(implicant_table)):
        for j in range(len(implicant_table[i])):
            for str,(minterms,isNotPrime) in implicant_table[i][j].items():
                if not isNotPrime:
                    prime_implicant_dict[str]=minterms
    return prime_implicant_dict

def search_result(minterms, implicant_set, prime_implicant_dict):
    """
    使用递归，搜索覆盖，先找出本质本源蕴含项，将剩余未用的蕴含项和未覆盖项递归调用该函数搜索
    :param minterms:要求覆盖的最小项
    :type minterms:set<int>
    :param implicant_set: 候选蕴含项集合
    :type implicant_set:set<str>
    :param prime_implicant_dict: 全部本源蕴含项的字典，键字符串，值是覆盖的最小项
    :type prime_implicant_dict: dict<str:set<int>>
    :return:返回由implicant_set中项覆盖给定minterms的集合
    :rtype:set<str>
    """
    result=set()
    #第一步，找本质本源蕴含项
    essential_implicant_set=set()#存储本质本源项
    essential_minitem_set=set()# 相应的最小项
    for minterm in minterms:
        found=0#覆盖该最小项的蕴含项数目
        curr_implicant=''
        for implicant in implicant_set:
            if minterm in prime_implicant_dict[implicant]:
                found+=1
                curr_implicant=implicant
                if found>=2:#有至少两个本源蕴含项可以覆盖，说明这个最小项上不存在本质本源
                    break
        if found==1:#覆盖该最小项的本源蕴涵项唯一，是本质本源
            essential_implicant_set.add(curr_implicant)
            essential_minitem_set.add(minterm)
            result.add(curr_implicant)
    implicant_set=implicant_set.difference(essential_implicant_set)
    for implicant in essential_implicant_set:#被本质本源覆盖的最小项不必再搜索覆盖
        minterms=minterms.difference(prime_implicant_dict[implicant])

    if len(minterms)==0:#全部覆盖完
        return result
    # 如果找到本质本源，可能还有去除以后还有新的本质本源，因此递归搜索
    if len(result)!=0:#说明找到了本质本源蕴涵项
        return result.union(search_result(minterms,implicant_set,prime_implicant_dict))
    #如果找不到本质本源，暴力搜索：枚举选择蕴含项，筛选最小项，再调用搜索得到结果，对不同蕴含项得到结果比较得出最好的返回
    else:
        best_implicant_set=implicant_set#得以覆盖剩余最小项的最小蕴含项集合
        for implicant in get_coverable_implicant(implicant_set,sorted(minterms)[0],prime_implicant_dict):
            curr_implicant_set={implicant}#包含implicant的最小蕴含项集合
            curr_minterms=minterms.difference(prime_implicant_dict[implicant])
            curr_implicant_set=curr_implicant_set.union(search_result(curr_minterms,implicant_set.difference({implicant}),prime_implicant_dict))
            if len(curr_implicant_set)<len(best_implicant_set):
                best_implicant_set=curr_implicant_set
        return result.union(best_implicant_set)


def quine_mccluskey(minterms,dcs,n_variables):
    """
    QM算法主函数
    :param mintems: 用最小项表示逻辑式，最小项的编号列表
    :param dcs: don't care项，输入函数前请将minterms和dc的交集从minterms中去除
    :param n_variables: 变元数量
    :type n_variables: int
    :type minterms: list<str>
    """
    #第一步，得到蕴含项表，取出其中标记为False的本源蕴含项
    implicant_table=get_implicant_table(minterms,dcs,n_variables)
    prime_implicant_dict=get_prime_implicant_dict(implicant_table)
    prime_implicant_set={str for str in prime_implicant_dict}#只包含字符串，不包括覆盖最小项信息
    #第二步，搜索覆盖
    result=search_result(set(minterms),prime_implicant_set,prime_implicant_dict)

    return result



if __name__=="__main__":
    test1=find_common('010-','011-')#should be '01--'
    result1=quine_mccluskey([4,8,5,6,9,10,13],[0,7,15],4)#10-0,1-01,01--
    #result1={'1-01','01--','10-0'}
    test_without_dont_care=quine_mccluskey([18,22,23,19,16,17,21,20,13],[], 5)#AB'+A'BCD'E
    #test_without_dont_care={'10---','01101'}
    result2=quine_mccluskey([6, 7, 8, 9, 10, 11, 12],[1,3,14],4)#A'C'+B'CD'+B'C'D
    #result2={'1--0','10--','011-'}程序给出了AD'+AB'+A'BC也正确且与上述答案项数一样
    result3=quine_mccluskey([0, 1, 8, 10, 11],[6, 9, 12, 13, 14],4)#AB'+B'C'
    #result3={'10--','-00-'}
    result4=quine_mccluskey([0, 5, 9, 14, 15],[1, 6, 7, 11],4)#A'B'C'+BC+A'BD+B'C'D
    #result4={'-11-','0-01','-001','000-'}
    pass
