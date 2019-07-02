import time

import attr
import click
import sunspec.core.client

import epcsunspecdemo.clishared
import epcsunspecdemo.utils


def send_val(point, val):
    point.value_setter(val)
    point.write()


def clear_faults(config):
    model = config.state.block.model
    model.read_points()
    s = config.state.value_getter()
    print(f'Inverter State: {s}')
    tries = 0
    while s == config.faulted_value:
        # clear faults
        send_val(config.cmd_point, config.cmd_flags.set(config.fault_clear))
        time.sleep(0.5)
        model.read_points()
        s = config.state.value_getter()
        print(f'Inverter State: {s}')
        tries += 1
        if tries > 10:
            raise Exception('Unable to clear faults!')
    # remove fault clear command
    send_val(config.cmd_point, config.cmd_flags.clear(config.fault_clear))


def demo(device, config, cycles):
    # Read common model
    device.common.read()
    print(device.common)

    device.model_17.read()
    print(device.model_17)

    config.model.read()
    print(config.model)
    # Set control source, if defined
    if config.ctl_src is not None:
        send_val(config.ctl_src, 1)

    # stop
    value = config.cmd_flags.clear_all()
    if config.invert_enable:
        value = config.cmd_flags.set(config.invert_enable)
    send_val(config.cmd_point, value)

    clear_faults(config=config)

    for ref in config.references:
        send_val(ref.point, ref.value)

    try:
        for _ in range(cycles):
            # enable and run
            value = config.cmd_flags.set(config.enable)
            send_val(config.cmd_point, value)
            print('{}: {}'.format(value, config.cmd_flags.active()))

            config.model.read()
            print(config.model)

            time.sleep(0.5)
    finally:
        # remove run command
        send_val(config.cmd_point, config.cmd_flags.clear(config.enable))
        # clear control source, if defined
        if config.ctl_src is not None:
            send_val(config.ctl_src, 0)

        print("controlset")

def gridtied_demo(device, invert_enable, cycles):
    points = device.epc_control.model.points
    refs =  [
        Reference(point=points['CmdV'], value=480),
        Reference(point=points['CmdHz'], value=60),
        Reference(point=points['CmdRealPwr'], value=10000), #10kW
        Reference(point=points['CmdReactivePwr'], value=5000), #5kVA
    ]
    config = DeviceConfig(
        cmd_point=device.epc_control.model.points['CmdBits'],
        cmd_flags=epcsunspecdemo.utils.Flags(
            model=device.epc_control,
            point='CmdBits',
        ),
        enable='En',
        fault_clear='FltClr',
        invert_enable='InvertHwEnable',
        references=refs,
        ctl_src=device.epc_control.model.points['CtlSrc'],
        model=device.epc_control,
        state=device.inverter.model.points['StVnd'],
        faulted_value=3,
    )

    demo(device=device, config=config, cycles=cycles)


def dcdc_demo(device, invert_enable, cycles):
    config = DeviceConfig(
        cmd_point=device.epc_control.model.points['CmdBits'],
        cmd_flags=epcsunspecdemo.utils.Flags(
            model=device.epc_control,
            point='CmdBits',
        ),
        enable='En',
        fault_clear='FltClr',
        invert_enable='InvertHwEnable',
        references=[
            References(
                point=device.epc_control.model.points['CmdVout'],
                value=800
            )
        ],
        ctl_src=device.epc_control.model.points['CtlSrc'],
        model=device.epc_control,
        state=device.epc_control.model.points['St'],
        faulted_value=3,
    )

    demo(device=device, config=config, cycles=cycles)


def abb_demo(device, invert_enable, cycles):
    points = device.abb_control.model.points
    refs =  [
        Reference(point=points['ABBCmdV'], value=480),
        Reference(point=points['ABBCmdHz'], value=60),
        Reference(point=points['ABBCmdRealPower'], value=10000), #10kW
        Reference(point=points['ABBCmdReactivePower'], value=5000), #5kVA
    ]
    config = DeviceConfig(
        cmd_point=device.abb_control.model.points['ABBCmdBits'],
        cmd_flags=epcsunspecdemo.utils.Flags(
            model=device.abb_control,
            point='ABBCmdBits',
        ),
        enable='Enable',
        fault_clear='FaultReset',
        invert_enable=None,
        references=refs,
        ctl_src=None,
        model=device.abb_control,
        state=device.abb_control.model.points['ABBActiveState'],
        faulted_value=3, #probably wrong
    )

    demo(device=device, config=config, cycles=cycles)


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


@attr.s
class Reference:
    point = attr.ib()
    value = attr.ib()


@attr.s
class DeviceConfig:
    cmd_point = attr.ib()
    cmd_flags = attr.ib()
    enable = attr.ib()
    fault_clear = attr.ib()
    invert_enable = attr.ib()
    references = attr.ib()
    ctl_src = attr.ib()
    model = attr.ib()
    state = attr.ib()
    faulted_value = attr.ib()