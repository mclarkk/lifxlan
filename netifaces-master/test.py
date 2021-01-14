import netifaces

print('Found interfaces:')
for iface in netifaces.interfaces():
    print('  %s' % iface)

print('')

for iface in netifaces.interfaces():
    allAddrs = netifaces.ifaddresses(iface)

    print('Interface %s:' % iface)

    for family in allAddrs:
        addrs = allAddrs[family]
        fam_name = netifaces.address_families[family]
        print('  Address family: %s' % fam_name)
        for addr in addrs:
            print('    Address  : %s' % addr['addr'])
            nmask = addr.get('netmask', None)
            if nmask:
                print('    Netmask  : %s' % nmask)
            bcast = addr.get('broadcast', None)
            if bcast:
                print('    Broadcast: %s' % bcast)

    print('')

print('Found gateways:')
gateway_info = netifaces.gateways()
for family in gateway_info:
    if family == 'default':
        continue

    fam_name = netifaces.address_families[family]
    print('  Family: %s' % fam_name)
    for gateway,interface,default in gateway_info[family]:
        if default:
            def_text = ', default'
        else:
            def_text = ''
        print('    %s (via %s%s)' % (gateway, interface, def_text))
    print('')
    
print('Default gateways:')
default_gateways = gateway_info['default']
for family in default_gateways:
    fam_name = netifaces.address_families[family]
    gateway, interface = default_gateways[family]
    print('  %s: %s (via %s)' % (fam_name, gateway, interface))
