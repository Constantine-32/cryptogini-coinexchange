
exclude_coins = True
check_volumes = False
record_coins_txt = False

#Tracked coins

market = 'BTC'
coins_to_exclude = []

#Spikes
spikes_alarms = [-0.7,-0.1, 0.7, 0.05, 0.02, 0.005]

#Time events
t_betw_fetch = 0.5
t_betw_rec = 6
t_betw_res_alarm = 20
t_pump_duration = 20

#Pump
next_pump = {'year': 2018, 'month': 1, 'day': 27, 'hour' : 19, 'min' : 00, 'sec' : 00, 'group': "Mega_Pump", 'ended' : False}
make_order = True
pump_time_margin = 5 # -t when bot will start the pump proceduree

btc_available = 0
perc_to_pump = 0.9

pump_percentage = 0.03
pump_change_sell = 1.12
pump_change_abort = 0.1
