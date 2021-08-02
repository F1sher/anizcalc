det_num = 4
t_spk_num = 12
tsum_spk_num = t_spk_num // 2

histo_size = 4096 #(chanels)

histo_finisize = 512
histo_fsize = 16384 #(bytes)
histo_en_fnames = ["BUFKA" + str(i) + ".SPK" for i in range(1, det_num+1)]
histo_t_fnames = ["TIME" + str(i) + ".SPK" for i in range(1, t_spk_num+1)]
