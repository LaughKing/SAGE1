#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "operator/vector_store_sink_operator.h"

namespace py = pybind11;

void BindVectorStoreSinkOperator(py::module& m) {
    // VectorStoreConfig struct binding
    py::class_<sage_flow::VectorStoreConfig>(m, "VectorStoreConfig")
        .def(py::init<>())
        .def_readwrite("collection_name", &sage_flow::VectorStoreConfig::collection_name_)
        .def_readwrite("batch_size", &sage_flow::VectorStoreConfig::batch_size_)
        .def_readwrite("update_index", &sage_flow::VectorStoreConfig::update_index_);
    
    // VectorStoreSinkOperator class binding
    py::class_<sage_flow::VectorStoreSinkOperator, sage_flow::Operator>(m, "VectorStoreSinkOperator")
        .def(py::init<sage_flow::VectorStoreConfig>(),
             "Create vector store sink operator with config")
        .def("process", &sage_flow::VectorStoreSinkOperator::process,
             "Process input record and store in vector database")
        .def("open", &sage_flow::VectorStoreSinkOperator::open,
             "Open vector store sink operator")
        .def("close", &sage_flow::VectorStoreSinkOperator::close,
             "Close vector store sink operator")
        .def("get_message_count", &sage_flow::VectorStoreSinkOperator::getMessageCount,
             "Get total number of messages stored in vector database");
    
    // Factory function binding
    m.def("CreateVectorStoreSink", &sage_flow::CreateVectorStoreSink,
          "Create vector store sink operator with collection name, batch size, and update index flag",
          py::arg("collection_name"), 
          py::arg("batch_size") = 100, 
          py::arg("update_index") = true);
}
