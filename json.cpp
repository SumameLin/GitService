    QJsonArray jsonArry;
    for(auto var : varList)
    {
       QStringList varsplit = var.split(".");
       QVector<QJsonArray> vectorArry(6);
       getVectorArry(varsplit, vectorArry);
       int length(0);
       QStringList nameList;
       for(auto i : jsonArry)
       {
           auto obj = i.toObject();
           nameList << obj["name"].toString();
       }
       if(!nameList.contains(vectorArry[0].first().toObject()["name"].toString()))
       {
           jsonArry.append(vectorArry[0].first().toObject());
       }
       else
           diguiJson(length, varsplit.length(), jsonArry, vectorArry);
    }

void TTranslator::getVectorArry(QStringList &varList, QVector<QJsonArray> &vectorArry)
{
    int depth = varList.length();
    for (int j = depth - 1; j >= 0; j--)
    {
        if(j == (varList.length() - 1))
        {
            QJsonObject lastObj;
            lastObj["name"] = varList[j];
            lastObj["addr"] = "MB2000";
            lastObj["size"] = "word";
            vectorArry[j].append(lastObj);
        }
        else
        {
            QJsonObject nodeObj;
            nodeObj["name"] = varList[j];
            nodeObj["subType"] = vectorArry[j + 1];
            vectorArry[j].append(nodeObj);
        }
    }
}

void TTranslator::diguiJson(int &length,const  int dataLength, QJsonArray &childrenArr, QVector<QJsonArray> &vectorArry)
{
    if(length <= dataLength)
    {
        length += 1;
        QStringList nameList;
        int iCount(0);
        for(auto i : childrenArr)
        {
            auto obj = i.toObject();
            if(obj["name"].toString() == vectorArry[length -1].first().toObject()["name"].toString())
            {
                QJsonArray node1Arry = obj["subType"].toArray();
                QStringList nameList;
                for(auto i1 : node1Arry)
                {
                    auto obj1 = i1.toObject();
                    nameList << obj1["name"].toString();
                }
                if(!nameList.contains(vectorArry[length].first().toObject()["name"].toString()))
                {
                    node1Arry.append(vectorArry[length].first().toObject());
                }
                else
                {
                    diguiJson(length, dataLength, node1Arry, vectorArry);
                }
                obj["subType"] = node1Arry;
                childrenArr.replace(iCount, obj);
            }
            iCount +=1;
        }
    }
}