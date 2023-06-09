# Setting Up the Development Environment

## Installing Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
```

Activate the new PATH environment variable:

```bash
source $HOME/.cargo/env
```

For the Windows platform, you can go to the following official download address and download according to the prompts:

```
https://www.rust-lang.org/tools/install
```

## Installing Binaryen

* Install version >= 99 of `binaryen`:
  * [Debian/Ubuntu](https://tracker.debian.org/pkg/binaryen): `apt-get install binaryen`
  * [Homebrew](https://formulae.brew.sh/formula/binaryen): `brew install binaryen`
  * [Arch Linux](https://archlinux.org/packages/community/x86_64/binaryen/): `pacman -S binaryen`
  * Windows: [Binary releases can be downloaded](https://github.com/WebAssembly/binaryen/releases)

## Creating a Virtual Python Environment for Testing

```bash
python3 -m venv ~/env
source ~/env/bin/activate
python3 -m pip install --upgrade pip
```

The next time you want to use the test environment, simply run the following command again.

```bash
source ~/env/bin/activate
```

## Installing the EOS Testing Framework

Install ipyeos:

```bash
python3 -m pip install -U ipyeos
```

If your platform is Windows or MacOSX M1/M2, you also need to download an image that includes the ipyeos tool:

```bash
docker pull ghcr.io/uuosio/ipyeos:latest
```

On macOS, the recommended software for installing and running Docker is [OrbStack](https://orbstack.dev/download). For other platforms, you can use [Docker Desktop](https://www.docker.com/products/docker-desktop).

## Installing the Rust Smart Contract Builder

```bash
python3 -m pip install -U rust-contracts-builder
```

## Installing the EOS Python Toolkit

```bash
python3 -m pip install -U pyeoskit
```

pyeoskit is used for deploying contracts to the mainnet or testnet.

## Checking the Environment

Create a new Rust contract project:

```bash
rust-contract init hello
```

Build:

```bash
cd hello
rust-contract build
```

Test:

```bash
ipyeos -m pytest -s -x test.py -k test_hello
```

If your are using Windows or macOS M1/M2, or on other platforms using the ARM instruction set, the above command will run the test in docker.

Alternatively, you can run `cargo test` to run the tests:

```bash
cargo test
```

When running `cargo test`, the tests defined in `lib.rs` will be executed:

```rust
#[test]
fn test_inc() {
    let mut tester = ChainTester::new();
    //uncomment the following line to enable contract debugging.
    // tester.enable_debug_contract("hello", true).unwrap();

    deploy_contract(&mut tester);
    update_auth(&mut tester);

    let permissions = r#"
    {
        "hello": "active"
    }
    "#;
    tester.push_action("hello", "inc", "".into(), permissions).unwrap();
    tester.produce_block();

    tester.push_action("hello", "inc", "".into(), permissions).unwrap();
    tester.produce_block();
}
```

Note that before running `cargo test`, you must first execute the `eosdebugger` application available in `ipyeos`. The Rust test code needs to connect to `eosdebugger` to run the tests.

If your are using Windows or on platforms using the ARM instruction set, `eosdebugger` will run in docker.

After starting `eosdebugger`, run `cargo test`, and you will see the following output in the `eosdebugger` console:

```bash
[(hello,inc)->hello]: CONSOLE OUTPUT BEGIN =====================
count is 1

[(hello,inc)->hello]: CONSOLE OUTPUT END   =====================
debug 2023-05-24T09:18:36.315 ipyeos    controller.cpp:2498           clear_expired_input_ ] removed 0 expired transactions of the 50 input dedup list, pending block time 2018-06-01T12:00:04.000
debug 2023-05-24T09:18:36.319 ipyeos    apply_context.cpp:40          print_debug          ] 
[(hello,inc)->hello]: CONSOLE OUTPUT BEGIN =====================
count is 2

[(hello,inc)->hello]: CONSOLE OUTPUT END   =====================
```
