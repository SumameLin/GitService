void TTranslator::findJson(QStringList &varList, QJsonArray &vectorObj1)
{
    QVector<QJsonArray> vectorObj(6);
    int depth = varList.length();
    for (int j = depth - 1; j >= 0; j--)
    {
        if(j == (varList.length() - 1))
        {
            QJsonObject lastObj;
            lastObj["name"] = varList[j];
            lastObj["addr"] = "MB2000";
            lastObj["size"] = "word";
            vectorObj[j].append(lastObj);
        }
        else
        {
            QJsonObject nodeObj;
            nodeObj["name"] = varList[j];
            nodeObj["subType"] = vectorObj[j + 1];
            vectorObj[j].append(nodeObj);
        }
    }
    QStringList nameList;
    for(auto i : vectorObj1)
    {
        auto obj = i.toObject();
        nameList << obj["name"].toString();
    }
    if(!nameList.contains(vectorObj[0].first().toObject()["name"].toString()))
    {
        vectorObj1.append(vectorObj[0].first().toObject());
    }
    else
    {
        //第一层有相同 Application
        int iCount(0);
        for(auto i : vectorObj1)
        {
            auto obj = i.toObject();
            if(obj["name"].toString() == vectorObj[0].first().toObject()["name"].toString())
            {
                QJsonArray node1Arry = obj["subType"].toArray();
                QStringList nameList;
                for(auto i1 : node1Arry)
                {
                    auto obj1 = i1.toObject();
                    nameList << obj1["name"].toString();
                }
                if(!nameList.contains(vectorObj[1].first().toObject()["name"].toString()))
                {
                    node1Arry.append(vectorObj[1].first().toObject());
                    obj["subType"] = node1Arry;
                    vectorObj1.replace(iCount, obj);
                }
                else
                {
                    //第一层有相同 gHmiData
                    int iCount2(0);
                    for(auto i2 : node1Arry)
                    {
                        auto obj2 = i2.toObject();
                        if(obj2["name"].toString() == vectorObj[1].first().toObject()["name"].toString())
                        {
                            QJsonArray node2Arry = obj2["subType"].toArray();
                            QStringList nameList;
                            for(auto i3 : node2Arry)
                            {
                                auto obj3 = i3.toObject();
                                nameList << obj3["name"].toString();
                            }
                            if(!nameList.contains(vectorObj[2].first().toObject()["name"].toString()))
                            {
                                node2Arry.append(vectorObj[2].first().toObject());
                                obj2["subType"] = node2Arry;
                                node1Arry.replace(iCount2, obj2);
                                obj["subType"] = node1Arry;
                                vectorObj1.replace(iCount, obj);
                            }
                            else
                            {
                                //第一层有相同 stDraw_Charge
                                int iCount4(0);
                                for(auto i4 : node2Arry)
                                {
                                    auto obj4 = i4.toObject();
                                    if(obj4["name"].toString() == vectorObj[2].first().toObject()["name"].toString())
                                    {
                                        QJsonArray node3Arry = obj4["subType"].toArray();
                                        QStringList nameList;
                                        for(auto i5 : node3Arry)
                                        {
                                            auto obj5 = i5.toObject();
                                            nameList << obj5["name"].toString();
                                        }
                                        if(!nameList.contains(vectorObj[3].first().toObject()["name"].toString()))
                                        {
                                            node3Arry.append(vectorObj[3].first().toObject());
                                            obj4["subType"] = node3Arry;
                                            node2Arry.replace(iCount4, obj4);
                                            obj2["subType"] = node2Arry;
                                            node1Arry.replace(iCount2, obj2);
                                            obj["subType"] = node1Arry;
                                            vectorObj1.replace(iCount, obj);
                                        }
                                    }
                                    iCount4 +=1;
                                }
                            }
                        }
                        iCount2+=1;
                    }
                }
            }
            iCount +=1;
        }
    }
}