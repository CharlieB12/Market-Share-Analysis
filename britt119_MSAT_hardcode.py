'''
Charlie Britt
Manual MSAT
'''

import arcpy

#environment
src_ws = r'C:\Users\cbrit\Documents\GEOG5223\Week6\libraries_data_sources'

out_path = r'C:\Users\cbrit\Documents\GEOG5223\Week6'
out_name = 'MSATout.gdb'
out_ws = out_path + '\\' + out_name

if not arcpy.Exists(out_ws):
    arcpy.management.CreateFileGDB(out_path, out_name)
    
arcpy.env.workspace = out_ws

scratch = arcpy.env.scratchGDB

arcpy.env.overwriteOutput = True

#input, output, parameters

point = src_ws + '\\' + 'public_library_shp'
polygon = src_ws + '\\' + 'trt00_shp'
table = src_ws + '\\' + 'population'

unique_field = 'NAME'
join_field = 'STFID2'
area_field = 'Area'
table_join = 'GEO_ID'
table_pop = 'P001001'

out_feature = 'market_share'

#Create thiessen polygons
desc = arcpy.da.Describe(polygon)
arcpy.env.extent = desc['extent']

out_thiessen = scratch + '/thiessen_tmp'
arcpy.analysis.CreateThiessenPolygons(point, out_thiessen, 'ALL')

print(arcpy.Exists(out_thiessen))

#intersect thiessen polygon with tracts
intersect = scratch + '/intersect_tmp'
arcpy.analysis.Intersect([out_thiessen, polygon], intersect, 'ALL')

print(arcpy.Exists(intersect))

#join intersection with population
arcpy.management.JoinField(intersect, join_field, table, table_join, [table_pop])

#get proportions
new_pop = 'NewPop'
formula = f'!{table_pop}! * !Shape_Area! / !{area_field}!'
arcpy.management.CalculateField(intersect, new_pop, formula, field_type='DOUBLE',
                                expression_type='PYTHON3')

#Dissolve joined layer
dissolve = out_ws + '/tract_dissolve'
arcpy.management.Dissolve(intersect, dissolve, unique_field,
                          statistics_fields=[(new_pop, "SUM")])

#get population total
total = 0
cursor = arcpy.da.SearchCursor(dissolve, ['SUM_NewPop'])
for row in cursor:
    total+=row[0]

#compute percent population
percentage = 'PctPop'
pct_formula = f'(!SUM_NewPop! / {total}) * 100'
arcpy.management.CalculateField(dissolve, percentage, pct_formula, field_type='DOUBLE',
                                expression_type='PYTHON3')
