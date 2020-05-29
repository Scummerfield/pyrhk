# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 13:49:58 2020

@author: Alex
"""

# import libraries

from enum import Enum
import struct


class RHK:

    def __init__(self,filename): # initialisation method

        self.fid = open(filename,"rb") # open the file in read module
        self.raw_data = bytearray(self.fid.read()) # read all bytes from file
        self.fid.close() # close the file
        self.offset = 0 # setting the offset counter to 0

        self.header = self.read_file_header() # read in the file header
        self.page_index_header = self.get_object(self.header['object_list'][0]) # get the page index header
        self.page_index = self.get_page_index()
        self.pages = [] # empty container for each page

        for i in range(self.header['total_page_count']): # for each page

            page = dict() # empty dict for the page
            thumbnail_exists = False # flag for checking if there is a thumnail

            index = self.page_index[i] # get the index listing for the current page

            page['header'] = self.get_object(index['object_list'][0],data_type = index['page_data_type'])

            # load the page data from the page index list

            for listing in index['object_list']:
                if listing['object_ID'] == 4: # page data
                    page['data'] = self.get_object(listing,params = page['header']['params'],data_type = index['page_data_type'])
                elif listing['object_ID'] == 16: # thumbnail Header
                    page['thumbnail_header'] = self.get_object(listing)
                else:
                    pass

            for listing in index['object_list']: # go back a second time and load the thumnail if the header data exists
                if listing['object_ID'] == 14: # thumbnail data
                    if 'thumbnail_header' in page: # only load if the header exists
                        page['thumbnail'] = self.get_object(listing,page['thumbnail_header'])
                        # rescale thumnail data
                        thumbnail_exists = True # set thumbnail exists flag to True

            if not thumbnail_exists: # if there is no thumnail data then generate it from the page data
                page['thumbnail'] = page['data'] # use the page data to generate thumbnail as it's low res
                thumbnail_exists = True


            self.pages.append(page) # append the page to the array

        self.raw_data = [] # empty the raw_data array to save memory

    # Class methods for extracting metadata


    def read_file_header(self): # reading in the file header


        self.offset = 0 # set offset to 0 as required for the start of the file

        file_header = dict() # empty dict for holding header information

        file_header['f_head_size'] = self.readb(2)
        file_header['f_signature'] = self.reads(2,strLen = 18)
        file_header['total_page_count'] = self.readb(4)
        file_header['object_list_count'] = self.readb(4)
        file_header['object_field_size'] = self.readb(4)
        file_header['reserved_bytes'] = self.readb(8) # reserved for future use

        file_header['object_list'] = self.get_object_list(file_header['object_list_count'])

        return file_header

    def get_object_list(self,n_objects): # method for reading object lists

        object_list = [] # empty container for object list

        for i in range(n_objects):

            OL = dict() # empty dict for object listed

            OL['object_ID'] = self.readb(4)
            OL['object_offset'] = self.readb(4)
            OL['object_size'] = self.readb(4)

            # only load object if not undefined and it has finite size/offset
            if (OL['object_ID'] != 0) & (OL['object_offset']*OL['object_size'] != 0):
                object_list.append(OL) # append the dict to the object list
            else:
                pass
        return object_list # return final object list to the header

    def get_object(self,object_listing,params = [],data_type = []):

        # required arguments

        # object_listing is a standard object listing from the end of a header/index

        # optional arguments

        # 'params' is an optional argument contatining a dict of values for different object types e.g. list of strings etc
        # data_type is an extra flag for loading page


        id = object_listing['object_ID']

        self.offset = object_listing['object_offset']

        if object_listing['object_size']*self.offset != 0: # check there is something to load

            # generic classs for retrieving objects

            if id == 0: # undefined object
                object = []
            elif id == 1: # page index header
                object = self.get_page_index_header()
            elif id == 2: # page index array
                object = self.get_page_index()
            elif id == 3: # page header
                object = self.get_page_header(params)
            elif id == 4: # page data
                object = self.load_page_data(params,data_type) # loading a data page using the parameters from the header
            elif id == 5: # image drift header
                object = self.load_image_drift_header()
            elif id == 6: # image drift
                object = self.load_image_drift()
            elif id == 7: # spec drift header
                object = self.load_spec_drift_header()
            elif id == 8: # spec drift data
                object = self.load_spec_drift_data(params)
            elif id == 9: # colour info
                object = self.load_color_info()
            elif id == 10: # string data
                object = self.load_string_data(params)
            elif id == 11: # tip track header
                object = self.load_tip_track_header()
            elif id == 12: # tip track data
                object = self.load_tip_track_data()
            elif id == 13: # PRM
                object = self.load_PRM()
            elif id == 14: # Thumbnail
                object = self.load_thumbnail(params)
            elif id == 15: # PRM header
                object = self.load_PRM_header()
            elif id == 16: # Thumbnail Header
                object = self.load_thumbnail_header()
            elif id == 17: # API Info
                object = self.load_api_info()
            elif id == 18: # History info
                object = self.load_history_info()
            elif id == 19: # Piezo Sensitivity
                object = self.load_piezo_sensitivity()
            elif id == 20: # Frequency Sweep Data
                object = self.load_frequency_sweep_data()
            elif id == 21: # Scan Processor Info
                object = self.load_scan_processor_info()
            elif id == 22: # PLL Info
                object = self.load_pll_info()
            elif id == 23: # CH1 Drive Info
                object = self.load_ch1_drive_info()
            elif id == 24: # CH2 Drive Info
                object = self.load_ch2_drive_info()
            elif id == 25: # Lockin0 Info
                object = self.load_lockin0_info()
            elif id == 26: # Lockin1 Info
                object = self.load_lockin1_info()
            elif id == 27: # ZPI Info
                object = self.load_zpi_info()
            elif id == 28: # KPI Info
                object = self.load_kpi_info()
            elif id == 29: # Aux PI Info
                object = self.load_aux_pi_info()
            elif id == 30: # Low-pass Filter0 Info
                object = self.load_lowpass_filter0_info()
            elif id == 31: # Low-pass Filter1 Info
                object = self.load_lowpass_filter1_info()
            elif id == 32 : # load internal piezo modulation info_count
                object = self.load_piezo_modulation_info()
            elif id == 33:
                object = self.load_pll2_info()
            else:
                object = []
        else:
            object = []

        return object

    # Object Load Methods *****************

    # 1: page index header
    def get_page_index_header(self):

        page_index_header = dict()

        page_index_header['page_count'] = self.readb(4)
        page_index_header['object_list_count'] = self.readb(4)
        page_index_header['reserved_bytes'] = self.readb(8) # reserved 8 bytes for future use
        page_index_header['object_list'] = self.get_object_list(page_index_header['object_list_count'])

        return page_index_header

    # 2: page index
    def get_page_index(self):

        n_index = self.header['total_page_count'] # getting number of indexes

        page_index_array = []

        for i in range(n_index): # get index for each page

            page_index = dict()

            page_index['page_id'] = [self.readb(2) for j in range(8)] # get unique id for each page

            page_index['page_data_type'] = self.readb(4)
            page_index['page_source_type'] = self.readb(4)
            page_index['object_list_count'] = self.readb(4)
            page_index['minor_version'] = self.readb(4)

            page_index['object_list'] = self.get_object_list(page_index['object_list_count'])

            page_index_array.append(page_index)

        return page_index_array

    # 3. Page header
    def get_page_header(self,data_type):

        page_header = dict() # empty dict for page header

        if data_type == 6: # if the page data type is a sequential data page

            page_header['data_type'] = self.readb(4)
            page_header['data_length'] = self.readb(4)
            page_header['param_count'] = self.readb(4)
            page_header['object_list_count'] = self.readb(4)
            page_header['data_info_size'] = self.readb(4)
            page_header['data_info_string_count'] = self.readb(4)


        else: # read a normal header type

            # list of attributes to automate byte read calls

            # format: ['attribute_description',n_bytes,read_type]
            # 'attribute_description' : description of variable
            # n_bytes : number of bytes to read for val
            # read_type : type of variabel 0 = int, 1 = float

            attrs  = [
            ['field_size',2,0],
            ['string_count',2,0],
            ['page_type',4,0],
            ['data_sub_source',4,0],
            ['line_type',4,0],
            ['nX',4,0],
            ['nY',4,0],
            ['nWidth',4,0],
            ['nHeight',4,0],
            ['image_type',4,0],
            ['scan',4,0],
            ['group_ID',4,0],
            ['page_data_size',4,0],
            ['minimum_z_value',4,0],
            ['maximum_z_value',4,0],
            ['x_scale',4,1],
            ['y_scale',4,1],
            ['z_scale',4,1],
            ['xy_scale',4,1],
            ['x_offset',4,1],
            ['y_offset',4,1],
            ['z_offset',4,1],
            ['period',4,1],
            ['bias',4,1],
            ['current',4,1],
            ['angle',4,1],
            ['color_infolist_count',4,0],
            ['grid_x_size',4,0],
            ['grid_y_size',4,0],
            ['object_list_count',4,0],
            ['data_32',1,0], # 32-bit data flag 1 for true
            ['reserved_flags',3,0],
            ['reserved_bytes',60,0] # reserved bytes for future use
            ]

            page_header['params'] = dict()

            for attr in attrs: # loop through attrs list

                if attr[2] == 0: # read int value
                    page_header['params'][attr[0]] = self.readb(attr[1])
                elif attr[2] == 1: # read float value
                    page_header['params'][attr[0]] = self.readf(attr[1])
                else:
                    continue

        # Load the data objects

        page_header['object_list'] = self.get_object_list(page_header['params']['object_list_count'])

        # loading the objects into a dictionary

        page_header['objects'] = dict()

        for listing in page_header['object_list']:

            try:
                    page_header['objects'][object_type(listing['object_ID']).name] = self.get_object(listing,page_header['params'])
            except:
                    page_header['objects']['Uknown Object'] = []


        if data_type == 6: # if the data type is sequential data page then load the data info

            data_info = []

            for param in range(page_header['param_count']):

                info = dict()

                info['param_gain'] = self.readf(4)
                info['str_label'] = self.reads(2)
                info['str_unit'] = self.reads(2)

                data_info.append(info)

            page_header['data_info'] = data_info

        else:
            pass


        return page_header

    # 4. Page Data
    def load_page_data(self,params,data_type):

        page_data = []

        if data_type == 0: # image data

            width = params['nWidth']
            height = params['nHeight']

            # reading in main data array and scaling at the same time

            page_data = [[self.readb(4)*params['z_scale'] for point in range(width)] for step in range(height)]


        elif data_type == 1: # line/spectral data

            points = params['nWidth']
            nSpectra = params['nHeight']

            if (params['line_type'] in [1,6,9,10,11,13,18,19,21,22]):

                page_data = [[self.readf(4)*params['z_scale'] for point in range(points)] for spectra in range(nSpectra)]
            else:
                page_data = [[self.readb(4)*params['z_scale'] for point in range(points)] for spectra in range(nSpectra)]


            # insert code to read sweep info after the main data

        elif data_type == 2: # xy data
            page_data = []
        elif data_type == 3: # annotated_line_spectral_data
            page_data = []
        elif data_type == 4: # text_data
            page_data = []
        elif data_type == 5: # text_annotate
            page_data = []
        elif data_type == 6: # sequential_data THIS NEEDS WORK

            width = params['nWidth']
            height = params['nHeight']

            page_data = [self.readf(4) for value in range(width*height)]

            print('Sequential Data Page!') # alert that a sequential data page is present

            page_data = []
        else:
            page_data = []

        return page_data

    # 5. Image drift header
    def load_image_drift_header(self):

        image_drift_header = dict()

        image_drift_header['start_time'] = self.readb(8)
        image_drift_header['drift_option'] = self.readb(4)

        return image_drift_header

    # 6. image_drift
    def load_image_drift(self):

        image_drift = dict()

        image_drift['time'] = self.readf(4)
        image_drift['dX'] = self.readf(4)
        image_drift['dY'] = self.readf(4)
        image_drift['CumulativedX'] = self.readf(4)
        image_drift['CumulativedY'] = self.readf(4)
        image_drift['XRate'] = self.readf(4)
        image_drift['YRate'] = self.readf(4)

        return image_drift

    # 7. Spec_drift_header
    def load_spec_drift_header(self):

        spec_drift_header = dict()

        spec_drift_header['start_time'] = self.readb(8)
        spec_drift_header['drift_option'] = self.readb(4)
        spec_drift_header['string_count'] = self.readb(4)
        spec_drift_header['channel'] = self.reads(2,strLen = spec_drift_header['string_count'])

        return spec_drift_header

    # 8. spec drift data
    def load_spec_drift_data(self,params):

        if (params['page_type'] in [16,38,37,39]):

            spec_drift_data = [] # empty container for sdrift data

            for i in range(params['nHeight']): # for every spectra load the postion and drift info
                sdd = dict()

                sdd['time'] = self.readf(4)
                sdd['XCoord'] = self.readf(4)
                sdd['YCoord'] = self.readf(4)
                sdd['dX'] = self.readf(4)
                sdd['dY'] = self.readf(4)
                sdd['CumulativedX'] = self.readf(4)
                sdd['CumulativedY'] = self.readf(4)

                spec_drift_data.append(sdd)

        return spec_drift_data

    # 9. colour information
    def load_color_info(self):

        color_info = dict()

        color_info['struct_size'] = self.readb(2)
        color_info['reserved'] = self.readb(2)

        color_info['HSVStart'] = dict()
        color_info['HSVStart']['H'] = self.readf(4)
        color_info['HSVStart']['S'] = self.readf(4)
        color_info['HSVStart']['V'] = self.readf(4)

        color_info['HSVEnd'] = dict()
        color_info['HSVEnd']['H'] = self.readf(4)
        color_info['HSVEnd']['S'] = self.readf(4)
        color_info['HSVEnd']['V'] = self.readf(4)

        color_info['ClrDirection'] = self.readb(4)
        color_info['num_entries'] = self.readb(4)
        color_info['StartSlidePos'] = self.readf(4)
        color_info['EndSlidePos'] = self.readf(4)

        color_info['ColorTransform'] = dict() # colour transform struct

        color_info['ColorTransform']['Gamma'] = self.readf(4)
        color_info['ColorTransform']['Alpha'] = self.readf(4)
        color_info['ColorTransform']['Xstart'] = self.readf(4)
        color_info['ColorTransform']['Xstop'] = self.readf(4)
        color_info['ColorTransform']['Ystart'] = self.readf(4)
        color_info['ColorTransform']['Ystop'] = self.readf(4)
        color_info['ColorTransform']['Ystart'] = self.readf(4)
        color_info['ColorTransform']['MappingMode'] = self.readb(4)
        color_info['ColorTransform']['Invert'] = self.readb(4)

        return color_info

    # 10. string data
    def load_string_data(self,params):

        n_strings = params['string_count']

        strings = dict() # empty dict for strings

        for i in range(n_strings):
            strings[text_string_labels(i)] = self.reads(2)

        return strings


    # 11. tip track header
    def load_tip_track_header(self):

        TTH = dict()

        TTH['filetime'] = self.readb(8)
        TTH['feature_height'] = self.readf(4)
        TTH['feature_width'] = self.readf(4)
        TTH['time_constant'] = self.readf(4)
        TTH['cycle_rate'] = self.readf(4)
        TTH['phase_lag'] = self.readf(4)

        TTH['string_count'] = self.readb(4)
        TTH['tip_track_info_count'] = self.readb(4)

        for i in range(TTH['string_count']):
            TTH['channel'] = self.reads(2)

        return TTH

    # 12. tip track data
    def load_tip_track_data(self,info_count):

        array = []
        TTD = dict()

        for i in range(info_count):

            TTD['cumulative_time'] = self.readf(4)
            TTD['time'] = self.readf(4)
            TTD['dx'] = self.readf(4)
            TTD['dy'] = self.readf(4)

            array.append(TTD)

        return array

    # 13. PRM
    def load_PRM(self,data_length):

        PRM = [self.readb(4) for i in range(data_length)]

        return PRM

    # 14. Thumbnail
    def load_thumbnail(self,header):

        thumbnail = [[self.readb(4) for point in range(header['width'])] for step in range(header['height'])]

        return thumbnail

    # 15. PRM Header
    def load_PRM_header(self):

        PRM_header = dict()

        PRM_header['compression_flag'] = self.readb(4)
        PRM_header['data_size'] = self.readb(8)
        PRM_header['compression_size'] = self.readb(8)

        return PRM_header

    # 16. Thumnail header
    def load_thumbnail_header(self):

        thumbnail_header = dict()

        thumbnail_header['width'] = self.readb(4)
        thumbnail_header['height'] = self.readb(4)
        thumbnail_header['format'] = self.readb(4)

        return thumbnail_header

    # 17. API information
    def load_api_info(self):

        api_info = dict()

        api_info['Hi'] = self.readf(4)
        api_info['Lo'] = self.readf(4)
        api_info['Gain'] = self.readf(4)
        api_info['Offset'] = self.readf(4)

        return api_info

    # 18. history information
    def load_history_info(self):

        history_info = dict()

        history_info['string_count'] = self.readb(4)
        history_info['history_path'] = self.reads(2)
        history_info['Pixel2timeFile'] = self.reads(2)

        return history_info

    # 19. Piezo Sensitivity
    def load_piezo_sensitivity(self):

        piezo_sensitivity = dict()

        piezo_sensitivity['tube_x_sensitivity'] = self.readf(8)
        piezo_sensitivity['tube_y_sensitivity'] = self.readf(8)
        piezo_sensitivity['tube_z_sensitivity'] = self.readf(8)
        piezo_sensitivity['tube_z_offset_sensitivity'] = self.readf(8)
        piezo_sensitivity['scan_x_sensitivity'] = self.readf(8)
        piezo_sensitivity['scan_y_sensitivity'] = self.readf(8)
        piezo_sensitivity['scan_z_sensitivity'] = self.readf(8)
        piezo_sensitivity['actuator_sensitivity'] = self.readf(8)

        piezo_sensitivity['string_count'] = self.readb(4)

        string_array = [
        'tube_x_unit',
        'tube_y_unit',
        'tube_z_unit',
        'tube_z_offset_unit',
        'scan_x_unit',
        'scan_y_unit',
        'scan_z_unit',
        'scan_actuator_unit',
        'tube_calibration',
        'scan_calibration',
        'actuator_calibration',
        ]

        for string in string_array:
            piezo_sensitivity[string] = self.reads(2)

        return piezo_sensitivity

    # 20. Frequency Sweep Data
    def load_frequency_sweep_data(self):

        FSD = dict()

        FSD['PSD_total_signal'] = self.readf(8)
        FSD['peak_frequency'] = self.readf(8)
        FSD['peak_amplitude'] = self.readf(8)
        FSD['drive_amplitude'] = self.readf(8)
        FSD['signal_to_drive_ratio'] = self.readf(8)
        FSD['q_factor'] = self.readf(8)

        FSD['string_count'] = self.readb(4)

        string_array = [
        'total_signal_unit',
        'peak_frequency_unit',
        'peak_amplitude_unit',
        'drive_amplitude_unit',
        'signal_to_drive_ratio_unit',
        'q_factor_unit',
        'peak_3db_width_unit'
        ]

        for string in string_array:
            FSD[string] = self.reads(2)

        return FSD

    # 21. scan processor information
    def load_scan_processor_info(self):

        SPI = dict()

        SPI['dx_slope_compensation'] = self.readf(8)
        SPI['dy_slope_compensation'] = self.readf(8)
        SPI['string_count'] = self.readb(4)

        string_array = [
        'xs_slope_compensation_unit',
        'ys_slope_compensation_unit'
        ]

        for string in string_array:
            SPI[string] = self.reads(2)

        return SPI

    # 22. PLL information
    def load_pll_info(self):

        pll_info = dict()

        pll_info['string_count'] = self.readb(4)
        pll_info['amplitude_control'] = self.readb(4)
        pll_info['drive_amplitude'] = self.readf(8)
        pll_info['drive_ref_frequency'] = self.readf(8)
        pll_info['lockin_freq_offset'] = self.readf(8)
        pll_info['lockin_harmonic_factor'] = self.readf(8)
        pll_info['lockin_pahse_offset'] = self.readf(8)
        pll_info['PLL_PI_gain'] = self.readf(8)
        pll_info['PLL_PI_int_cut_off_freq'] = self.readf(8)
        pll_info['PLL_PI_lower_bound'] = self.readf(8)
        pll_info['PLL_PI_upper_bound'] = self.readf(8)
        pll_info['diss_PI_gain'] = self.readf(8)
        pll_info['diss_PI_cut_off_freq'] = self.readf(8)
        pll_info['diss_PI_lower_bound'] = self.readf(8)
        pll_info['diss_PI_upper_bound'] = self.readf(8)

        string_array = [
        'lockin_filter_cutoff_freq',
        'drive_amplitude_unit',
        'drive_frequency_unit',
        'lockin_freq_offset_unit',
        'lockin_phase_unit',
        'PLL_PI_gain_unit',
        'PLL_PI_ICF_unit',
        'PLL_PI_output_unit',
        'PLL_PI_gain_unit',
        'diss_PI_gain_unit',
        'diss_PI_ICF_unit',
        'diss_PI_ouput_unit',
        'diss_pll_PI_setpoint_unit',
        'lockin_filter_roll_off',
        'drive_amplitude_control',
        'pll_lockguard_status',
        'lockin_cut_off_frequency_unit',
        'lockin_time_constant_unit'
        ]

        for string in string_array:
            pll_info[string] = self.reads(2)

        return pll_info

    # generic drive info methods

    def load_drive_info(self):

        DI = dict()

        DI['string_count'] = self.readb(4)
        DI['master_oscillator'] = self.readb(4)
        DI['amplitude'] = self.readf(8)
        DI['frequency'] = self.readf(8)
        DI['phase_offset'] = self.readf(8)
        DI['harmonic_factor'] = self.readf(8)

        string_array = [
        'amplitude_unit',
        'frequency_unit',
        'phase_offset_unit',
        'reserved_unit'
        ]

        for string in string_array:
            DI[string] = self.reads(2)

        return DI

    # 23. ch1 drive information
    def load_ch1_drive_info(self):

        DI = self.load_drive_info()

        return DI

    # 24. ch2 drive information
    def load_ch2_drive_info(self):

        DI = self.load_drive_info()

        return DI

    # generic lockin info load method

    def load_lockin_info(self):

        LI = dict()

        LI['string_count'] = self.readb(4)
        LI['non_master_oscillator'] = self.readb(4)
        LI['frequency'] = self.readf(8)
        LI['harmonic_factor'] = self.readf(8)
        LI['phase_offset'] = self.readf(8)

        string_array = [
        'filter_cutoff_freq',
        'freq_unit',
        'phae_unit'
        ]

        for string in string_array:
            LI[string] = self.reads(2)

        return LI

    # 25. lockin 0 info
    def load_lockin0_info(self):

        LI = self.load_lockin_info()

    # 26. lockin 1 info
    def load_lockin1_info(self):

        LI = self.load_lockin_info()

        return LI

    # general method for loading PI info
    def load_pi_info(self):

        PI = dict()

        PI['set_point'] = self.readf(8)
        PI['proportional_gain'] = self.readf(8)
        PI['integral_gain'] = self.readf(8)
        PI['lower_point'] = self.readf(8)
        PI['upper_bound'] = self.readf(8)
        PI['string_count'] = self.readb(4)

        string_array = [
        'feedback_type',
        'set_point_unit',
        'proportional_gain_unit',
        'integral_gain_unit',
        'output_unit'
        ]

        for string in string_array:
            PI[string] = self.reads(2)

        return PI

    # 27. zpi_info
    def load_zpi_info(self):

        zpi_info = self.load_pi_info()

        return zpi_info

    # 28. kpi information
    def load_kpi_info(self):

        kpi_info = self.load_pi_info()

        return kpi_info

    # 29. aux pi info
    def load_aux_pi_info(self):

        aux_pi_info = self.load_pi_info()

        return aux_pi_info

    # generic low-pass info load method

    def load_low_pass_info(self):

        LP = dict()

        LP['string_count'] = self.readb(4)
        LP['cutoff_frequency'] = self.reads(2)

        return LP

    # 30. Low-pass filter0 info
    def load_lowpass_filter0_info(self):

        filter_info = self.load_low_pass_info()

        return filter_info

    # 31. Low-pass filter1 info
    def load_lowpass_filter1_info(self):

        filter_info = self.load_low_pass_info()

        return filter_info

    # 32. Internal Piezo modulation info
    def load_piezo_modulation_info(self):

        MI = dict()

        MI['string_count'] = self.readb(4)
        MI['non_master_oscillator'] = self.readb(4)
        MI['amplitude'] = self.readf(8)
        MI['harmonic_factor'] = self.readf(8)
        MI['frequency'] = self.readf(8)
        MI['phase_offset'] = self.readf(8)

        MI['amplitude_unit'] = self.reads(2)
        MI['freq_unit'] = self.reads(2)
        MI['phase_unit'] = self.reads(2)

        return MI

    # 33. load pll2 info_count
    def load_pll2_info(self):

        pll_info = self.load_pll_info()

        return pll_info


    # class methods *****************************

    # utility functions for reading bytes into values and strings

    def readb(self,nBytes): # read value from variable number of bytes //   carry on here!!!    

        value = RHK.parseb([val for val in self.raw_data[self.offset:self.offset+nBytes]])

        self.offset += nBytes # advancing the offset counter

        return value

    def parseb(barray):

        byte = sum([barray[idx] << 8*idx for idx in range(len(barray))])

        return byte

    def readf(self,nBytes): # read float value

        if nBytes == 4: # single precision float
            value = struct.unpack('f',self.raw_data[self.offset:self.offset+nBytes])[0] # returns as 1 element list so use first element as value
        elif nBytes == 8: # i.e. double precision float
            value = struct.unpack('d',self.raw_data[self.offset:self.offset+nBytes])[0] # returns as 1 element list so use first element as value
        else:
            value = 0.0

        self.offset += nBytes  # advancing the offset counter

        return value

    def readc(self,nBytes):

        character = chr(self.readb(self.raw_data,idx,nBytes))
        self.offset += nBytes  # advancing the offset counter

        return character

    def reads(self,nBytes,strLen = 0): # reading in a string, automatically determine string length if not given as argument

        if strLen ==0:
            strLen = self.readb(2)
        else:
            pass

        chrVals = [self.readb(nBytes) for i in range(strLen)]
        final_string = ''.join([chr(val) for val in chrVals])

        # offset update not needed as handled by readb method

        return final_string


# type definition for objects, pages etc.

class object_type(Enum):

    undefined                   = 0
    page_index_header           = 1
    page_index_array            = 2
    page_header                 = 3
    page_data                   = 4
    image_drift_header          = 5
    image_drift                 = 6
    spec_drift_header           = 7
    spec_drift_data             = 8
    color_info                  = 9
    string_data                 = 10
    tip_track_header            = 11
    tip_track_data              = 12
    prm                         = 13
    thumbnail                   = 14
    prm_header                  = 15
    thumbnail_header            = 16
    api_info                    = 17
    history_info                = 18
    piezo_sensitivity           = 19
    frequency_sweep_data        = 20
    scan_processor_info         = 21
    pll_info                    = 22
    ch1_drive_info              = 23
    ch2_drive_info              = 24
    lockin0_info                = 25
    lockin1_info                = 26
    zpi_info                    = 27
    kpi_info                    = 28
    aux_pi_info                 = 29
    low_pass_filter0_info       = 30
    low_pass_filter1_info       = 31
    piezo_modulation_info       = 32
    pll2_info                   = 33

class page_data_type(Enum):

    image_data                      = 0
    line_spectral_data              = 1
    xy_data                         = 2
    annotated_line_spectral_data    = 3
    text_data                       = 4
    text_annotate                   = 5
    sequential_data                 = 6

class page_source_type(Enum):

    raw_page            = 0
    processed_page      = 1
    calculated_page     = 2
    imported_page       = 3

class page_type(Enum):

    undefined                       = 0
    topographic_image               = 1
    current_image                   = 2
    aux_image                       = 3
    force_image                     = 4
    signal_image                    = 5
    image_FFT_transform             = 6
    noise_power_spectrum            = 7
    line_test                       = 8
    oscilloscope                    = 9
    IV_spectra                      = 10
    image_IV_4x4                    = 11
    image_IV_8x8                    = 12
    image_IV_16x16                  = 13
    image_IV_32x32                  = 14
    image_IV_centre                 = 15
    image_interactive_spectra       = 16
    autocorrelation_page            = 17
    IZ_spectra                      = 18
    gain_4_topography               = 19
    gain_8_topography               = 20
    gain_4_current                  = 21
    gain_8_current                  = 22
    image_iv_64x64                  = 23
    autocorrelation_spectrum        = 24
    counter_data                    = 25
    multichannel_analyzer_data      = 26
    AFM_data_using_RHK_AFM_100      = 27
    CITS                            = 28
    GPIB                            = 29 # Not used
    video_channel                   = 30 # Not used
    image_out_spectra               = 31
    Idatalog                        = 32 # Not used
    I_Ecset                         = 33 # Not used
    I_Ecdata                        = 34 # Not used
    I_DSP_AD                        = 35 # Not used
    Discrete_spectroscopy           = 36
    image_and_discrete_spectroscopy = 37
    ramp_spectroscopy               = 38
    discrete_spectroscopy           = 39

class line_type(Enum):

    not_a_line                      = 0
    histogram                       = 1
    cross_section                   = 2
    line_test                       = 3
    oscilloscope                    = 4
    reserved                        = 5
    noise_power_spectrum            = 6
    iv_spectrum                     = 7
    iz_spectrum                     = 8
    image_x_average                 = 9
    image_y_average                 = 10
    noise_autocorrelation_spectrum  = 11
    multichannel_analyzer_data      = 12
    renormalized_iv_data_from_variable_gap_iv   = 13
    image_histogram_spectra         = 14
    image_cross_section             = 15
    image_average                   = 16
    image_cross_section_Gsection    = 17
    image_out_spectra               = 18
    datalog_spectrum                = 19 # Not used
    Gxy                             = 20
    electrochemistry                = 21
    discrete_spectroscopy           = 22
    data_logger                     = 23
    time_spectroscopy               = 24
    zoom_FFT                        = 25
    frequency_sweep                 = 26
    phase_rotate                    = 27
    fiber_sweep                     = 28

class image_type(Enum):

    normal_image            = 0
    autocorrelation_image   = 1

class scan_direction(Enum):

    right       = 0
    left        = 1
    up          = 2
    down        = 3

def text_string_labels(string_number):

    string_labels = [
    'strLabel',
    'strSystemText',
    'strSessionText',
    'strUserText',
    'strPath',
    'strDate',
    'strTime',
    'strXUnits',
    'strYUnits',
    'strZUnits',
    'strXLabel',
    'strYLabel',
    'strStatusChannelText',
    'strCompletedLineCount',
    'strOverSamplingCount',
    'strSlicedVoltage',
    'strPLLProStatus',
    'strSetpointUnit',
    'stCHDriveValues']

    return string_labels[string_number]

# End of definition of pyRHK module
