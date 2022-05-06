import xlwt
from django.shortcuts import render
import mysql.connector as sql
import cx_Oracle
from django.http import HttpResponse
import csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from datetime import datetime

def getConnection():
    # connection = cx_Oracle.connect("WMSuser/software@localhost:1521/XEPDB1")
    connection = cx_Oracle.connect("FOXWMS/Password@117.232.114.195:1521/xe")
    # connection = sql.connect(host="localhost", port="3306", user="root", password="software", database="wmsreports")
    # connection = sql.connect(host="wmsreportdb.cynpun7qvuxw.ap-south-1.rds.amazonaws.com", port="3306", user="admin", password="Soft5632", database="wmsreports")
    return connection


def login(request):
    if request.method == "POST":
        try:
            global login
            con = getConnection()
            cur = con.cursor()
            lId = request.POST['lid']
            lPass = request.POST['lpass']
            query = 'Select * from "user" where username=' + "'" + lId + "'" 'and userpass=' + "'" + lPass + "'"
            # query = 'Select * from user where username=' + "'" + lId + "'" 'and userpass=' + "'" + lPass + "'"
            cur.execute(query)
            tup = tuple(cur.fetchall())
            if tup==():
                return render(request, 'login.html', {'errors': 'Login Failed!'})
            else:
                login = 'Yes'
                return render(request, 'home.html', {'name': lId})
        except Exception as e:
            return render(request, 'login.html', {'errors': e})


def home(request):
    return render(request, 'login.html', {'name': 'User'})


def reportsHome(request):
    return render(request, 'home.html')


def logout(request):
    login = 'No'
    return render(request, 'login.html', {'name': ''})


def inventory(request):
    try:
        if login == 'Yes':
            batchdata = getBatchNo()
            materialdata = getMaterialType()
            manufacturingdata = getManufacturingLine()
            palletdata = getPalletStatus()
            return render(request, 'inventoryreport.html', {'batchdata': batchdata,
                                                            'materialdata': materialdata,
                                                            'manufacturingdata': manufacturingdata,
                                                            'palletdata': palletdata})
        else:
            return render(request, 'login.html', {'name': ''})
    except Exception as e:
        return render(request, 'inventoryreport.html', {'Status': e})


def getBatchNo():
    con = getConnection()
    cur = con.cursor()
    sqlquery = 'select MIN("BatchNo") from "M_PalletList" where "RackLocationID" < 3265 and' \
               ' "BatchDttm" is not null GROUP BY "BatchNo" order by "BatchNo"'
    # sqlquery = 'select MIN(BatchNo) from M_PalletList where RackLocationID < 3265 and' \
    #             ' BatchDttm is not null GROUP BY BatchNo order by BatchNo'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def getMaterialType():
    con = getConnection()
    cur = con.cursor()
    sqlquery = 'select "MaterialID", "MaterialCode" from "M_Material"'
    # sqlquery = 'select MaterialTypeID, MaterialType from M_MaterialType'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def getManufacturingLine():
    con = getConnection()
    cur = con.cursor()
    sqlquery = 'select * from "M_MfgLine"'
    # sqlquery = 'select * from M_MfgLine'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def getPalletStatus():
    con = getConnection()
    cur = con.cursor()
    sqlquery = 'select * from "M_PalletStatus"'
    # sqlquery = 'select * from M_PalletStatus'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def InventoryReports(request):
    if request.method == "POST":
        try:
            global SummaryRecord, AllRecord
            con = getConnection()
            cur = con.cursor()
            batchId = request.POST.get('selectBatch')
            materialTypeCode = request.POST.get('selectMaterial')
            manufacturingLineId = request.POST.get('selectManufacturing')
            palletStatusId = request.POST.get('selectPellet')

            Filter1 = ""

            if batchId != None:
                Filter1 = Filter1 + ' and "BatchNo" =' + "'" + batchId + "'"
            if materialTypeCode != None:
                Filter1 = Filter1 + ' and "MaterialID" =' + materialTypeCode
            if manufacturingLineId != None:
                Filter1 = Filter1 + ' and "M_Material"."MfgLineID" =' + manufacturingLineId
            if palletStatusId != None:
                Filter1 = Filter1 + ' and "M_PalletList"."PalletStatus" =' + palletStatusId

            AllQuery = 'select "BatchNo", "BatchDttm", "PalletNumber", "MaterialCode", "MaterialType", "MaterialDesc", "CartonsOnPallet",' \
                       ' "M_MfgLine"."MfgLineNumber", "M_PalletStatus"."PalletStatus", "M_PalletList"."LabNo", "M_PalletList"."ProductionTime"' \
                       ' from "M_PalletList"' \
                       ' Inner join "M_Material" Using("MaterialID")' \
                       ' Inner join "M_MaterialType" Using("MaterialTypeID")' \
                       ' Inner join "M_MfgLine" on "M_MfgLine"."MfgLineID" = "M_Material"."MfgLineID"'\
                       ' Inner join "M_PalletStatus" on "M_PalletList"."PalletStatus" = "M_PalletStatus"."PalletStatusID"' \
                       ' where "RackLocationID" < 3265 and "BatchDttm" is not null' + Filter1 + ' order by "BatchNo"'

            # if batchId != None:
            #     Filter1 = Filter1 + ' and BatchNo =' + "'" + batchId + "'"
            # if materialTypeCode != None:
            #     Filter1 = Filter1 + ' and MaterialID =' + materialTypeCode
            # if manufacturingLineId != None:
            #     Filter1 = Filter1 + ' and M_Material.MfgLineID =' + manufacturingLineId
            # if palletStatusId != None:
            #     Filter1 = Filter1 + ' and M_PalletList.PalletStatus =' + palletStatusId
            #
            # AllQuery = 'select BatchNo, BatchDttm, PalletNumber, MaterialCode, MaterialType, MaterialDesc, CartonsOnPallet,' \
            #            ' M_MfgLine.MfgLineNumber, M_PalletStatus.PalletStatus, M_PalletList.LabNo, M_PalletList.ProductionTime' \
            #            ' from M_PalletList' \
            #            ' Inner join M_Material Using(MaterialID)' \
            #            ' Inner join M_MaterialType Using(MaterialTypeID)' \
            #            ' Inner join M_MfgLine on M_MfgLine.MfgLineID = M_Material.MfgLineID'\
            #            ' Inner join M_PalletStatus on M_PalletList.PalletStatus = M_PalletStatus.PalletStatusID' \
            #            ' where RackLocationID < 3265 and BatchDttm is not null' + Filter1 + ' order by BatchNo'

            Filter2 = ""
            if batchId != None:
                Filter2 = Filter2 + ' and "BatchNo" =' + "'" + batchId + "'"
            if materialTypeCode != None:
                Filter2 = Filter2 + ' and "MaterialID" =' + materialTypeCode
            if palletStatusId != None:
                Filter2 = Filter2 + ' and "M_PalletList"."PalletStatus" =' + palletStatusId

            SubQuery = 'select "BatchNo", "MaterialCode", Count(*) AS "'" + Load + "'", "CartonsOnPallet",' \
                       ' "M_PalletStatus"."PalletStatus" from "M_PalletList"' \
                       ' Inner join "M_Material" Using("MaterialID")' \
                       ' Inner join "M_PalletStatus" on "M_PalletList"."PalletStatus" = "M_PalletStatus"."PalletStatusID"' \
                       ' where "RackLocationID" < 3265 and "BatchDttm" is not null' + Filter2 + \
                       ' group by "BatchNo", "MaterialCode", "CartonsOnPallet", "M_PalletStatus"."PalletStatus"' \
                       ' order by "BatchNo"'

            # if batchId != None:
            #     Filter2 = Filter2 + ' and BatchNo =' + "'" + batchId + "'"
            # if materialTypeCode != None:
            #     Filter2 = Filter2 + ' and MaterialID =' + materialTypeCode
            # if palletStatusId != None:
            #     Filter2 = Filter2 + ' and M_PalletList.PalletStatus =' + palletStatusId
            #
            # SubQuery = 'select BatchNo, MaterialCode, Count(*) AS "'" + Load + "'", CartonsOnPallet,' \
            #            ' M_PalletStatus.PalletStatus from M_PalletList' \
            #            ' Inner join M_Material Using(MaterialID)' \
            #            ' Inner join M_PalletStatus on M_PalletList.PalletStatus = M_PalletStatus.PalletStatusID' \
            #            ' where RackLocationID < 3265 and BatchDttm is not null' + Filter2 + \
            #            ' group by BatchNo, MaterialCode, CartonsOnPallet, M_PalletStatus.PalletStatus' \
            #            ' order by BatchNo'

            cur.execute(SubQuery)
            SummaryRecord = tuple(cur.fetchall())

            cur.execute(AllQuery)
            AllRecord = tuple(cur.fetchall())

            if SummaryRecord == ():
                return render(request, 'report.html', {'errors': 'Records not found!'})
            else:
                return render(request, 'report.html', {'SummaryRecord': SummaryRecord, 'AllRecord': AllRecord})
        except Exception as e:
            return render(request, 'report.html', {'errors': e})


def downloadReport(request):
    if request.method == "POST":
        try:
           format = request.POST.get('selectDownloadFormat')
           if format != None:
               if format == "EXCEL":
                   response = HttpResponse(content_type='text/csv')
                   response['Content-Disposition'] = 'attachment; filename=Inventory Report.xls'
                   wb = xlwt.Workbook(encoding='utf-8')

                   ws = wb.add_sheet('Sub Report')
                   row_num = 0
                   font_style = xlwt.XFStyle()
                   font_style.font.bold = True
                   subColumns = ['BatchNo', 'Material Code', 'Load', 'Cartons', 'Pallet Status']

                   for col_num in range(len(subColumns)):
                       ws.write(row_num, col_num, subColumns[col_num], font_style)

                   font_style = xlwt.XFStyle()
                   for subRows in SummaryRecord:
                       row_num +=1
                       for col_num in range(len(subRows)):
                           ws.write(row_num, col_num, str(subRows[col_num]), font_style)

                   ws1 = wb.add_sheet('All Report')
                   row_num1 = 0
                   font_style1 = xlwt.XFStyle()
                   font_style1.font.bold = True
                   allColumns = ['BatchNo', 'Batch Date', 'Pallet No', 'Material Code', 'Material Type',
                                    'Material Name', 'Cartons on Pallet', 'Line No', 'Pallet Status', 'Lab No',
                                    'Production Time']

                   for col_num in range(len(allColumns)):
                       ws1.write(row_num1, col_num, allColumns[col_num], font_style1)

                   font_style1 = xlwt.XFStyle()
                   for allRows in AllRecord:
                       row_num1 += 1
                       for col_num in range(len(allRows)):
                           ws1.write(row_num1, col_num, str(allRows[col_num]), font_style1)

                   wb.save(response)
                   return response

               if format == "CSV":
                   response = HttpResponse(content_type='text/csv')
                   response['Content-Disposition'] = 'attachment; filename=Inventory Report.csv'

                   writer = csv.writer(response)

                   # writer.writerow(['Inventory Report'])
                   # writer.writerow(['Banaskantha District Co-operative Milk Producers Union Ltd.'])
                   # writer.writerow(['Banas Dairy, Post Box 20, Palanpur, Gujarat, India'])
                   # writer.writerow(['Phone :- 91-2742-253881 to 253885.'])
                   # writer.writerow(['Fax:- (02742) 252723. Report Generated Date:' + date.today().isoformat()])

                   writer.writerow(['BatchNo', 'Material Code',	'Load', 'Cartons', 'Pallet Status'])
                   for result in SummaryRecord:
                       writer.writerow([result[0], result[1], result[2], result[3], result[4]])

                   writer.writerow(['BatchNo', 'Batch Date', 'Pallet No', 'Material Code', 'Material Type',
                                    'Material Name', 'Cartons on Pallet', 'Line No', 'Pallet Status', 'Lab No',
                                    'Production Time'])
                   for result in AllRecord:
                       writer.writerow([result[0], result[1], result[2], result[3], result[4], result[5], result[6]
                                        , result[7], result[8], result[9], result[10]])

                   return response

               if format == "PDF":
                   filename = 'Inventory.pdf'
                   pdf = SimpleDocTemplate(filename)
                   now = datetime.now()

                   flow_obj = []

                   img_data=Image("BanasBanner.PNG", 400, 50)
                   t2 = Table([[img_data]])
                   t2style = TableStyle(
                       [("GRID", (0, 0), (-1, -1), .5, colors.black)])
                   t2.setStyle(t2style)
                   flow_obj.append(t2)

                   t1Data = []
                   h1Data = []
                   h1Data.append('BatchNo')
                   h1Data.append('MaterialCode')
                   h1Data.append('Load')
                   h1Data.append('Cartons')
                   h1Data.append('PalletStatus')
                   t1Data.append(h1Data)

                   for data in SummaryRecord:
                       rowData = []
                       rowData.append(data[0])
                       rowData.append(data[1])
                       rowData.append(data[2])
                       rowData.append(data[3])
                       rowData.append(data[4])
                       t1Data.append(rowData)

                   t1 = Table(t1Data, colWidths=[35, 90, 20, 25, 35])
                   t1style = TableStyle(
                       [("GRID", (0, 0), (-1, -1), .5, colors.black), ("FONT", (0, 0), (-1, -1), "Helvetica", 5)])
                   t1.setStyle(t1style)
                   flow_obj.append(t1)

                   tData = []
                   hData = []
                   hData.append('BatchNo')
                   hData.append('BatchDate')
                   hData.append('PalletNo')
                   hData.append('MaterialCode')
                   hData.append('MaterialType')
                   hData.append('MaterialName')
                   hData.append('CartonsOnPallet')
                   hData.append('LineNo')
                   hData.append('PalletStatus')
                   hData.append('LabNo')
                   hData.append('ProductionTime')
                   tData.append(hData)

                   for data in AllRecord:
                       rowData = []
                       rowData.append(data[0])
                       rowData.append(data[1].strftime("%d/%m/%y"))
                       rowData.append(data[2])
                       rowData.append(data[3])
                       rowData.append(data[4])
                       rowData.append(data[5])
                       rowData.append(data[6])
                       rowData.append(data[7])
                       rowData.append(data[8])
                       rowData.append(data[9])
                       rowData.append(data[10])
                       tData.append(rowData)

                   t = Table(tData, colWidths=[35, 35, 30, 45, 45, 120, 45, 25, 35, 25, 55])
                   tstyle = TableStyle(
                       [("GRID", (0, 0), (-1, -1), .5, colors.black), ("FONT", (0, 0), (-1, -1), "Helvetica", 5)])
                   t.setStyle(tstyle)
                   flow_obj.append(t)
                   flow_obj.append(Paragraph('Inventory Report Downloaded Date ' + now.strftime("%d/%m/%y")))
                   pdf.build(flow_obj)

                   with open(filename) as f:
                       data = f.read()

                   response = HttpResponse(data, content_type='application/pdf')
                   response['Content-Disposition'] = 'attachment; filename=Inventory Report.pdf'
                   return response
        except Exception as e:
            return render(request, 'report.html', {'errors': e})


def getRackSummary():
    con = getConnection()
    cur = con.cursor()
    sqlquery = 'select "RackLocStatus", Count(*) AS "'" + Total + "'" from "M_RacklocStatus"' \
               ' Inner join "M_Rack" on "M_RacklocStatus"."RacklocStatusID" = "M_Rack"."RackLocStatusID"' \
               ' where "RackLocID" < 3265' \
               ' group by "M_RacklocStatus"."RackLocStatus"' \
               ' order by "M_RacklocStatus"."RackLocStatus"'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def getPalletSummary():
    con = getConnection()
    cur = con.cursor()
    sqlquery = 'select "M_PalletStatus"."PalletStatus", Count(*) AS "'" + Total + "'" from "M_PalletList"' \
               ' Inner join "M_PalletStatus" on "M_PalletList"."PalletStatus" = "M_PalletStatus"."PalletStatusID"' \
               ' where "RackLocationID" < 3265 and "BatchDttm" is not null' \
               ' group by "M_PalletStatus"."PalletStatus"' \
               ' order by "M_PalletStatus"."PalletStatus"'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def getOrderSummary():
    con = getConnection()
    cur = con.cursor()
    # sqlquery = 'select "M_MaterialType"."MaterialType", Count(*) AS "OrderedQty",' \
    #            ' TO_CHAR(TRUNC(TO_DATE("ReqEndDttm",'" 'YY-MM-DD' "')),'" 'YY-MM-DD' "') AS "OrderDate"' \
    #            ' from "UnloadingLogSmry"' \
    #            ' Inner join "M_Material" ON "M_Material"."MaterialID" = "UnloadingLogSmry"."MaterialID"' \
    #            ' Inner join "M_MaterialType" ON "M_MaterialType"."MaterialTypeID" = "M_Material"."MaterialTypeID"' \
    #            ' where "Delivered" = 1 AND "ReqEndDttm" >= sysdate - 7' \
    #            ' group by "M_MaterialType". "MaterialType", TO_CHAR(TRUNC(TO_DATE("ReqEndDttm",'" 'YY-MM-DD' "')),'" 'YY-MM-DD' "')' \
    #            ' order by TO_CHAR(TRUNC(TO_DATE("ReqEndDttm",'" 'YY-MM-DD' "')),'" 'YY-MM-DD' "')'

    sqlquery = 'select "M_MaterialType"."MaterialType", Count(*) AS "OrderedQty"' \
               ' from "UnloadingLogSmry"' \
               ' Inner join "M_Material" ON "M_Material"."MaterialID" = "UnloadingLogSmry"."MaterialID"' \
               ' Inner join "M_MaterialType" ON "M_MaterialType"."MaterialTypeID" = "M_Material"."MaterialTypeID"' \
               ' where "Delivered" = 1 AND "ReqEndDttm" >= sysdate - 30' \
               ' group by "M_MaterialType". "MaterialType"' \
               ' order by "M_MaterialType". "MaterialType"'
    cur.execute(sqlquery)
    tup = tuple(cur.fetchall())
    return tup


def GetSummary(request):
    try:
        PalletSummary = getPalletSummary()
        RackSummary = getRackSummary()
        OrderSummary = getOrderSummary()

        return render(request, 'home.html', {'PalletSummary': PalletSummary, 'RackSummary': RackSummary, 'OrderSummary': OrderSummary})
    except Exception as e:
        return render(request, 'home.html', {'Status': e})



