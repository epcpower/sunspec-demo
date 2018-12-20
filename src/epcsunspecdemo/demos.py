import sys
import time

import click
import serial.serialutil
import sunspec.core.client

import epcsunspecdemo.clishared
import epcsunspecdemo.utils


def update_cmd_bits(cmd_bits, device):
    device.epc_control.CmdBits = cmd_bits.to_int()
    print('{}: {}'.format(device.epc_control.CmdBits, cmd_bits.active()))
    device.epc_control.model.points['CmdBits'].write()
    device.epc_control.read()
    print(device.epc_control)
    time.sleep(0.5)
    device.inverter.read()
    print(device.inverter.StVnd)


def gridtied_demo(device, invert_enable, cycles):
    cmd_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='CmdBits',
    )

    # Read common model
    device.common.read()
    print(device.common)

    device.model_17.read()
    print(device.model_17)

    # Set Mobus as control source 0=CAN 1=Modbus
    device.epc_control.read()
    print(device.epc_control)
    device.epc_control.CtlSrc = 1
    device.epc_control.model.points['CtlSrc'].write()

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        cmd_bits.set('InvertHwEnable')
    else:
        cmd_bits.clear('InvertHwEnable')

    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # clear faults
    cmd_bits.set('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # remove fault clear command
    cmd_bits.clear('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    device.epc_control.CmdV = 480
    device.epc_control.CmdHz = 60
    device.epc_control.model.points['CmdV'].write()
    device.epc_control.model.points['CmdHz'].write()

    try:
        for _ in range(cycles):
            # enable and run
            cmd_bits.set('En')
            device.epc_control.CmdBits = cmd_bits.to_int()
            print('{}: {}'.format(device.epc_control.CmdBits, cmd_bits.active()))
            device.epc_control.CmdRealPwr = 10000  # 10kW
            device.epc_control.CmdReactivePwr = 5000  # 5kVA
            device.epc_control.model.points['CmdBits'].write()
            device.epc_control.model.points['CmdRealPwr'].write()
            device.epc_control.model.points['CmdReactivePwr'].write()

            device.epc_control.read()
            print(device.epc_control)

            time.sleep(0.5)
    finally:
        # remove run command
        cmd_bits.clear('En')
        update_cmd_bits(cmd_bits=cmd_bits, device=device)

        # return control to CAN:
        device.epc_control.CtlSrc = 0
        device.epc_control.model.points['CtlSrc'].write()

        print("controlset")


def dcdc_demo(device, invert_enable, cycles):
    cmd_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='CmdBits',
    )
    status_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='Evt1',
    )
    fault_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='FaultFlags',
    )
    warning_bits = epcsunspecdemo.utils.Flags(
        model=device.epc_control,
        point='WrnFlgs',
    )

    # Read common model
    device.common.read()
    print(device.common)

    print(device.models)

    # Set Mobus as control source 0=CAN 1=Modbus
    device.epc_control.read()
    print(device.epc_control)
    fault_bits.from_int(device.epc_control.FaultFlags)
    print('Faults: ' + str(fault_bits.active()))
    device.epc_control.CtlSrc = 1
    device.epc_control.model.points['CtlSrc'].write()

    # stop
    cmd_bits.clear_all()

    if invert_enable:
        cmd_bits.set('InvertHwEnable')
    else:
        cmd_bits.clear('InvertHwEnable')

    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # clear faults
    cmd_bits.set('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    # remove fault clear command
    cmd_bits.clear('FltClr')
    update_cmd_bits(cmd_bits=cmd_bits, device=device)

    status_bits.from_int(device.epc_control.Evt1)
    fault_bits.from_int(device.epc_control.FaultFlags)
    warning_bits.from_int(device.epc_control.WrnFlgs)

    print('Cmd bits: ' + str(cmd_bits.active()))
    print('Evt1: ' + str(status_bits.active()))
    print('Faults: ' + str(fault_bits.active()))
    print('Warnings: ' + str(warning_bits.active()))

    device.epc_control.CmdVout = 800
    try:
        for _ in range(cycles):
            # enable and run
            cmd_bits.set('En')
            device.epc_control.CmdBits = cmd_bits.to_int()
            # print('{}: {}'.format(device.epc_control.CmdBits, cmd_bits.active()))
            device.epc_control.model.points['CmdBits'].write()
            device.epc_control.model.points['CmdVout'].write()

            device.epc_control.read()
            status_bits.from_int(device.epc_control.Evt1)
            fault_bits.from_int(device.epc_control.FaultFlags)
            warning_bits.from_int(device.epc_control.WrnFlgs)
            print('State: ' + str(device.epc_control.St))
            print('Evt1: ' + str(status_bits.active()))
            print('Faults: ' + str(fault_bits.active()))
            print('Warnings: ' + str(warning_bits.active()))
            # print(device.epc_control)

            # time.sleep(0.5)
    finally:
        # remove run command
        cmd_bits.clear('En')
        update_cmd_bits(cmd_bits=cmd_bits, device=device)

        # return control to CAN:
        device.epc_control.CtlSrc = 0
        device.epc_control.model.points['CtlSrc'].write()

        print("controlset")


@click.group(
    help='Demo connection to a grid-tied converter',
)
@click.pass_obj
def gridtied(config):
    config.common = gridtied_demo


@click.group(
    help='Demo connection to a DCDC converter',
)
@click.pass_obj
def dcdc(config):
    config.common = dcdc_demo


invert_enable_option = click.option(
    '--invert-enable/--no-invert-enable',
    help='Invert the converters hardware enable input',
)

slave_id_option = click.option(
    '--slave-id',
    type=int,
    default=1,
    help='Node ID of the converter',
)

max_count_option = click.option(
    '--max-count',
    type=int,
    default=100,
    help='Maximum number of registers to be requested at once',
)

cycles_option = click.option(
    '--cycles',
    type=int,
    default=25,
    help='Number of demo cycles to run',
)


if sys.platform.startswith('win'):
    port_help = 'Name of the COM port'
else:
    port_help = 'Path to the serial device'


@click.command(
    help='Demo direct serial Modbus RTU connection',
)
@click.option(
    '--port',
    required=True,
    help=port_help,
)
@click.option(
    '--baudrate',
    type=click.Choice(
        str(rate)
        for rate in serial.serialutil.SerialBase.BAUDRATES
    ),
    default='9600',
    help='Serial baudrate',
)
@epcsunspecdemo.clishared.model_path_option
@invert_enable_option
@slave_id_option
@max_count_option
@cycles_option
@click.pass_obj
def serial(
        config,
        port,
        model_path,
        invert_enable,
        slave_id,
        max_count,
        baudrate,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(model_path):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            max_count=max_count,
            device_type=sunspec.core.client.RTU,
            name=port,
            baudrate=baudrate,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


@click.command(
    help='Demo Modbus TCP connection',
)
@click.option(
    '--address',
    required=True,
    help='The IP or host name of the converter',
)
@click.option(
    '--port',
    type=int,
    default=502,
    help='The TCP port on the converter',
)
@epcsunspecdemo.clishared.model_path_option
@invert_enable_option
@slave_id_option
@max_count_option
@cycles_option
@click.pass_obj
def tcp(
        config,
        ip,
        port,
        model_path,
        invert_enable,
        slave_id,
        max_count,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(model_path):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            max_count=max_count,
            device_type=sunspec.core.client.TCP,
            ipaddr=ip,
            ipport=port,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


def add_commands(group):
    group.add_command(gridtied, name='gridtied')
    group.add_command(dcdc, name='dcdc')

    for group in (gridtied, dcdc):
        group.add_command(serial)
        group.add_command(tcp)
