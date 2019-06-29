import time

import click
import sunspec.core.client

import epcsunspecdemo.clishared
import epcsunspecdemo.utils


def send_val(point, val):
    point.value_setter(val)
    point.write()


def demo(device, cmd_flags, ctl_src, refs, model, cycles):
    # Read common model
    device.common.read()
    print(device.common)

    device.serial.read()
    print(device.serial)

    model.read()
    print(model)
    # Set control source, if defined
    if ctl_src is not None:
        send_val(ctl_src, 1)

    # stop
    val = cmd_flags['flags'].clear_all()
    if cmd_flags['invert_enable']:
        val = cmd_flags['flags'].set(cmd_flags['invert_enable'])
    send_val(cmd_flags['point'], val)
    # clear faults
    send_val(cmd_flags['point'], cmd_flags['flags'].set(cmd_flags['fault_clear']))
    # remove fault clear command
    send_val(cmd_flags['point'], cmd_flags['flags'].clear(cmd_flags['fault_clear']))

    for ref in refs:
        send_val(*ref)

    try:
        for _ in range(cycles):
            # enable and run
            val = cmd_flags['flags'].set(cmd_flags['enable'])
            send_val(cmd_flags['point'], val)
            print('{}: {}'.format(val, cmd_flags['flags'].active()))

            model.read()
            print(model)

            time.sleep(0.5)
    finally:
        # remove run command
        send_val(cmd_flags['point'], cmd_flags['flags'].clear(cmd_flags['enable']))
        # clear control source, if defined
        if ctl_src is not None:
            send_val(ctl_src, 0)

        print("controlset")


def gridtied_demo(device, invert_enable, cycles):
    cmd_flags = {
        'point': device.epc_control.model.points['CmdBits'],
        'flags': epcsunspecdemo.utils.Flags(
            model=device.epc_control,
            point='CmdBits',
        ),
        'enable': 'En',
        'fault_clear': 'FltClr',
        'invert_enable': 'InvertHwEnable',
    }

    refs =  [
        (device.epc_control.model.points['CmdV'], 480),
        (device.epc_control.model.points['CmdHz'], 60),
        (device.epc_control.model.points['CmdRealPwr'], 10000), #10kW
        (device.epc_control.model.points['CmdReactivePwr'], 5000), #5kVA
    ]

    demo(
        device=device,
        cmd_flags=cmd_flags,
        ctl_src=device.epc_control.model.points['CtlSrc'],
        refs=refs,
        model=device.epc_control,
        cycles=cycles,
    )


def dcdc_demo(device, invert_enable, cycles):
    cmd_flags = {
        'point': device.epc_control.model.points['CmdBits'],
        'flags': epcsunspecdemo.utils.Flags(
            model=device.epc_control,
            point='CmdBits',
        ),
        'enable': 'En',
        'fault_clear': 'FltClr',
        'invert_enable': 'InvertHwEnable',
    }

    demo(
        device=device,
        cmd_flags=cmd_flags,
        ctl_src=device.epc_control.model.points['CtlSrc'],
        refs=[(device.epc_control.model.points['CmdVout'], 800)],
        model=device.epc_control,
        cycles=cycles,
    )


def abb_demo(device, invert_enable, cycles):
    cmd_flags = {
        'point': device.abb_control.model.points['ABBCmdBits'],
        'flags': epcsunspecdemo.utils.Flags(
            model=device.abb_control,
            point='ABBCmdBits',
        ),
        'enable': 'Enable',
        'fault_clear': 'FaultReset',
        'invert_enable': None,
    }

    refs =  [
        (device.abb_control.model.points['ABBCmdV'], 480),
        (device.abb_control.model.points['ABBCmdHz'], 60),
        (device.abb_control.model.points['ABBCmdRealPower'], 10000), #10kW
        (device.abb_control.model.points['ABBCmdReactivePower'], 5000), #5kVA
    ]

    demo(
        device=device,
        cmd_flags=cmd_flags,
        ctl_src=None,
        refs=refs,
        model=device.abb_control,
        cycles=cycles,
    )


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


@click.group(
    help='Demo connection to an ABB converter',
)
@click.pass_obj
def abb(config):
    config.common = abb_demo


invert_enable_option = click.option(
    '--invert-enable/--no-invert-enable',
    help='Invert the converters hardware enable input',
)

cycles_option = click.option(
    '--cycles',
    type=int,
    default=25,
    help='Number of demo cycles to run',
)


@click.command(
    help='Demo direct serial Modbus RTU connection',
)
@epcsunspecdemo.clishared.serial_port_option
@epcsunspecdemo.clishared.serial_baudrate_option
@epcsunspecdemo.clishared.timeout_option
@epcsunspecdemo.clishared.model_path_option
@invert_enable_option
@epcsunspecdemo.clishared.slave_id_option
@cycles_option
@click.pass_obj
def serial(
        config,
        port,
        timeout,
        model_path,
        invert_enable,
        slave_id,
        baudrate,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(model_path):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            device_type=sunspec.core.client.RTU,
            name=port,
            baudrate=baudrate,
            timeout=timeout,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


@click.command(
    help='Demo Modbus TCP connection',
)
@epcsunspecdemo.clishared.tcp_address_option
@epcsunspecdemo.clishared.tcp_port_option
@epcsunspecdemo.clishared.timeout_option
@epcsunspecdemo.clishared.model_path_option
@invert_enable_option
@epcsunspecdemo.clishared.slave_id_option
@cycles_option
@click.pass_obj
def tcp(
        config,
        address,
        port,
        timeout,
        model_path,
        invert_enable,
        slave_id,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(model_path):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            device_type=sunspec.core.client.TCP,
            ipaddr=address,
            ipport=port,
            timeout=timeout,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


def add_commands(group):
    group.add_command(gridtied, name='gridtied')
    group.add_command(dcdc, name='dcdc')
    group.add_command(abb, name='abb')

    for group in (gridtied, dcdc, abb):
        group.add_command(serial)
        group.add_command(tcp)
