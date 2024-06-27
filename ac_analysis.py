from lib import ng_raw_read, to_data_frames, get_column_as_array, lookup, view_headers, PlotManager,measure_ac_parameters

if __name__ == '__main__':
    dfs = to_data_frames(ng_raw_read('ota-5t_tb2_ac.raw'))
    
    
    # df = dfs[0]  # Get the first DataFrame
    # view_headers(df)

    # df = dfs[1]
    # view_headers(df)


    df = dfs[0]
    # view_headers(df)


    # print("{:e}".format(float(get_column_as_array(df,'ugf')[0])))
    freq = get_column_as_array(df,'frequency')
    vout_mag = get_column_as_array(df,'v(vout)')
    ac_parameters = measure_ac_parameters(freq, vout_mag)

    vout_mag = ac_parameters["vout_mag"]
    vout_db = ac_parameters["vout_db"]
    vout_phase_margin = ac_parameters["vout_phase_margin"]
    A0 = ac_parameters["A0"]
    A0_db = ac_parameters["A0_db"]
    UGF = ac_parameters["UGF"]
    PM = ac_parameters["PM"]
    BW_3dB = ac_parameters["BW_3dB"]
    GBW = ac_parameters["GBW"]
    
    print(f'BW = {"{:e}".format(abs(BW_3dB))}')
    print(f'A0_db = {"{:.2f}".format(abs(A0_db))}')
    print(f'UGF = {"{:e}".format(abs(UGF))}')

    pm = PlotManager(num_subplots=2, title='AC Analysis', xlabel='Frequency', ylabel='')

    # Initial plot
    pm.plot(freq, vout_db, label='Gain dB', subplot_index=0)
    pm.plot(freq, vout_phase_margin, label='Phase', subplot_index=1)
    pm.add_line(line_orientation='vertical', line_value=ac_parameters["BW_3dB"], line_label='BW 3dB', line_color='red')
    pm.add_line(line_orientation='vertical', line_value=ac_parameters["BW_3dB"], line_label='BW 3dB', line_color='red',subplot_index=1)
    pm.show()


    '''example Usage
    # Call the function with data
    ac_parameters = measure_ac_parameters(frequencies, vout)

    # Accessing the returned data
    vout_mag = ac_parameters["vout_mag"]
    vout_db = ac_parameters["vout_db"]
    vout_phase_margin = ac_parameters["vout_phase_margin"]
    A0 = ac_parameters["A0"]
    A0_db = ac_parameters["A0_db"]
    UGF = ac_parameters["UGF"]
    PM = ac_parameters["PM"]
    BW_3dB = ac_parameters["BW_3dB"]
    GBW = ac_parameters["GBW"]

    # Print the results
    print("vout_mag:", vout_mag)
    print("vout_db:", vout_db)
    print("vout_phase_margin:", vout_phase_margin)
    print("A0:", A0)
    print("A0_db:", A0_db)
    print("UGF:", UGF)
    print("PM:", PM)
    print("BW_3dB:", BW_3dB)
    print("GBW:", GBW)
    '''