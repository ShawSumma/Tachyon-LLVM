from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int64
# def run(llc):
#     llvm.initialize()
#     llvm.initialize_native_target()
#     llvm.initialize_native_asmprinter()
#     target = llvm.Target.from_default_triple()
#     target_machine = target.create_target_machine()
#     backing_mod = llvm.parse_assembly("")
#     engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
#     mod = llvm.parse_assembly(str(llc))
#     mod.verify()
#     engine.add_module(mod)
#     engine.finalize_object()
#     func_ptr = engine.get_function_address("main")
#     fn = CFUNCTYPE(c_int64, c_int64)(func_ptr)
#     fn()
module = ir.Module()
