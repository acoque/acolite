## def identify_bundle
## function to identify image that needs to be processed
## written by Quinten Vanhellemont, RBINS
## 2021-03-10
## modifications:

def identify_bundle(bundle, input_type = None):
    import os, glob, shutil, zipfile
    import acolite as ac

    zipped = False

    while input_type is None:
        if not os.path.exists(bundle): break ## exit loop if path does not exist

        ################
        ## Landsat
        try:
            mtl = glob.glob('{}/{}'.format(bundle, '*MTL.txt'))
            if len(mtl)>0:
                meta = ac.landsat.metadata_read(mtl[0])
                ## get relevant data from meta
                if 'PRODUCT_CONTENTS' in meta: pk = 'IMAGE_ATTRIBUTES'## COLL2
                elif 'PRODUCT_METADATA' in meta: pk = 'PRODUCT_METADATA'## COLL1
                spacecraft_id, sensor_id = meta[pk]['SPACECRAFT_ID'],meta[pk]['SENSOR_ID']
                if spacecraft_id in ['LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']:
                    input_type = 'Landsat'
                    break ## exit loop
        except:
            pass ## continue to next sensor
        ## end Landsat
        ################

        ################
        ## Sentinel-2
        try:
            safe_files = ac.sentinel2.safe_test(bundle)
            granule = safe_files['granules'][0]
            #grmeta = ac.sentinel2.metadata_granule(safe_files[granule]['metadata']['path'])
            meta, band_data= ac.sentinel2.metadata_scene(safe_files['metadata']['path'])
            if meta['SPACECRAFT_NAME'] in ['Sentinel-2A', 'Sentinel-2B']:
                input_type = 'Sentinel-2'
                break ## exit loop
        except:
            pass ## continue to next sensor
        ## end Sentinel-2
        ################

        ################
        ## Sentinel-3
        try:
            dfiles = glob.glob('{}/*.nc'.format(bundle))
            dfiles.sort()
            gatts = ac.shared.nc_gatts(dfiles[0])
            if 'OLCI Level 1b Product' in gatts['title']:
                input_type = 'Sentinel-3'
                break ## exit loop
            else:
                print(gatts['title'])
        except:
            pass ## continue to next sensor
        ## end Sentinel-3
        ################

        ################
        ## Pléiades/SPOT
        try:
            ifiles,mfiles,pifiles,pmfiles = ac.pleiades.bundle_test(bundle, listpan=True)
            mfiles_set = set(mfiles)
            for mfile in mfiles_set: meta = ac.pleiades.metadata_parse(mfile)
            if meta['satellite'] in ['Pléiades', 'SPOT']:
                input_type = 'Pléiades'
                break ## exit loop
        except:
            pass ## continue to next sensor
        ## end Pléiades/SPOT
        ################


        ################
        ## WorldView
        try:
            metafile = glob.glob('{}/{}'.format(bundle,'*.XML'))[0]
            meta = ac.worldview.metadata_parse(metafile)
            if meta['satellite'] in ['WorldView2', 'WorldView3']:
                input_type = 'WorldView'
                break ## exit loop
        except:
            pass ## continue to next sensor
        ## end WorldView
        ################

        ################
        ## Planet data
        ## unzip files if needed
        try:
            if bundle[-4:] == '.zip':
                zipped = True
                bundle_orig = '{}'.format(bundle)
                bundle,ext = os.path.splitext(bundle_orig)
                zip_ref = zipfile.ZipFile(bundle_orig, 'r')
                for z in zip_ref.infolist():
                    z.filename = os.path.basename(z.filename)
                    zip_ref.extract(z, bundle)
                zip_ref.close()

            ## test files
            files = ac.planet.bundle_test(bundle)
            metafile = files['metadata']['path']
            image_file = files['analytic']['path']
            meta = ac.planet.metadata_parse(metafile)
            if 'platform' in meta:
                input_type = 'Planet'
                break  ## exit loop
        except:
            pass ## continue to next sensor
        ## end Planet
        ################

        ################
        break ## exit loop

    ## remove the extracted bundle
    if (zipped) & (os.path.exists(bundle)):
        shutil.rmtree(bundle)
        bundle = '{}'.format(bundle_orig)

    ## return input_type
    return(input_type)
