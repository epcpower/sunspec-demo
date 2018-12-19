import argparse
import sys
import time

import epcsunspecdemo.utils
import sunspec.core.client


# d = client.SunSpecClientDevice(client.RTU, 1, 'COM1', max_count=10)
# d = sunspec.core.client.client.SunSpecClientDevice(client.TCP, 1, ipaddr='192.168.10.203', max_count=10)
# print(d.models)
#
# d.epc_control.read()
# print(d.epc_control)


def parse_args(*args):
    parser = argparse.ArgumentParser()

    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--ip')#, default='192.168.10.203')
    interface_group.add_argument('--serial-port')

    parser.add_argument('--models', default='models')
    parser.add_argument('--invert-hw-enable', action='store_true')

    return parser.parse_args(args)


def update_cmd_bits(cmd_bits, d):
    d.epc_control.CmdBits = cmd_bits.to_int()
    print('{}: {}'.format(d.epc_control.CmdBits, cmd_bits.active()))
    d.epc_control.model.points['CmdBits'].write()
    d.epc_control.read()
    print(d.epc_control)
    time.sleep(0.5)


def main(sys_argv):
    args = parse_args(*sys_argv)

    client_args = {
        'slave_id': 1,
        'max_count': 10,
    }

    if args.ip is not None:
        client_args['device_type'] = sunspec.core.client.TCP
        client_args['ipaddr'] = args.ip
    elif args.serial_port is not None:
        client_args['device_type'] = sunspec.core.client.RTU
        client_args['name'] = args.serial_port
        client_args['baudrate'] = '9600'

    with epcsunspecdemo.utils.fresh_smdx_path(args.models):
        d = sunspec.core.client.SunSpecClientDevice(**client_args)

    cmd_bits = epcsunspecdemo.utils.Flags(
        model=d.epc_control,
        point='CmdBits',
    )
    status_bits = epcsunspecdemo.utils.Flags(
        model=d.epc_control,
        point='Evt1',
    )
    fault_bits = epcsunspecdemo.utils.Flags(
        model=d.epc_control,
        point='FaultFlags',
    )
    warning_bits = epcsunspecdemo.utils.Flags(
        model=d.epc_control,
        point='WrnFlgs',
    )

    # Read common model
    d.common.read()
    print(d.common)
    
    print(d.models)

    # Set Mobus as control source 0=CAN 1=Modbus
    d.epc_control.read()
    print(d.epc_control)
    fault_bits.from_int(d.epc_control.FaultFlags)
    print('Faults: ' + str(fault_bits.active()))
    d.epc_control.CtlSrc = 1
    d.epc_control.model.points['CtlSrc'].write()

    # stop
    cmd_bits.clear_all()

    if args.invert_hw_enable:
        cmd_bits.set('InvertHwEnable')
    else:
        cmd_bits.clear('InvertHwEnable')

    update_cmd_bits(cmd_bits, d)

    # clear faults
    cmd_bits.set('FltClr')
    update_cmd_bits(cmd_bits, d)

    # remove fault clear command
    cmd_bits.clear('FltClr')
    update_cmd_bits(cmd_bits, d)
    
    status_bits.from_int(d.epc_control.Evt1)
    fault_bits.from_int(d.epc_control.FaultFlags)
    warning_bits.from_int(d.epc_control.WrnFlgs)
    
    print('Cmd bits: ' + str(cmd_bits.active()))
    print('Evt1: ' + str(status_bits.active()))
    print('Faults: ' + str(fault_bits.active()))
    print('Warnings: ' + str(warning_bits.active()))
    
    d.epc_control.CmdVout = 800
    try:     
        #for _ in range(2500):
        while True:
            # enable and run
            cmd_bits.set('En')
            d.epc_control.CmdBits = cmd_bits.to_int()
            #print('{}: {}'.format(d.epc_control.CmdBits, cmd_bits.active()))
            d.epc_control.model.points['CmdBits'].write()
            d.epc_control.model.points['CmdVout'].write()
      
            d.epc_control.read()
            status_bits.from_int(d.epc_control.Evt1)
            fault_bits.from_int(d.epc_control.FaultFlags)
            warning_bits.from_int(d.epc_control.WrnFlgs)
            print('State: '    + str(d.epc_control.St)     )
            print('Evt1: '     + str(status_bits.active()) )
            print('Faults: '   + str(fault_bits.active())  )
            print('Warnings: ' + str(warning_bits.active()))
            #print(d.epc_control)
      
            #time.sleep(0.5)
    finally:
        # remove run command
        cmd_bits.clear('En')
        update_cmd_bits(cmd_bits, d)

        # return control to CAN:
        d.epc_control.CtlSrc = 0
        d.epc_control.model.points['CtlSrc'].write()

        print("controlset")


def entry_point():
    sys.exit(main(sys.argv[1:]))
