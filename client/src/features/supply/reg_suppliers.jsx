import { useState } from 'react'

function RegSuppliers() {
    const [suppliers, setSuppliers] = useState([])
    const [formData, setFormData] = useState({
        name: '',
        contactPerson: '',
        email: '',
        phone: '',
        address: ''
    })
    
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }
    
    const handleSubmit = (e) => {
        e.preventDefault()

        const newSupplier = {
            id: Date.now(),
            ...formData
        }

        setSuppliers([...suppliers, newSupplier])

        setFormData({
            name: '',
            contactPerson: '',
            email: '',
            phone: '',
            address: ''
        })
    }   

    const handleDelete = (id) => {
        setSuppliers(suppliers.filter(supplier => supplier.id !== id))
    }

    return (
        <div className="suppliers-page">
            <h2>Register Suppliers</h2>
            <p>Manage your registered suppliers.</p>

            <form onSubmit={handleSubmit} className="supplier-form">
                <h3>Register New Supplier</h3>

                <input
                    type="text"
                    name="name"
                    placeholder="Supplier Name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                />

                <input
                    type="text"
                    name="contactPerson"
                    placeholder="Contact Person"
                    value={formData.contactPerson}
                    onChange={handleChange}
                    required
                />

                <input
                    type="email"
                    name="email"
                    placeholder="Email Address"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                <input
                    type="tel"
                    name="phone"
                    placeholder="Phone Number"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                />
                <input
                    type="text"
                    name="address"
                    placeholder="Supplier Address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                />
                <button type="submit">Register Supplier</button>
            </form>

            <div className="supplier-list">
                <h3>Supplier List</h3>

                {suppliers.length === 0 ? (
                    <p>No suppliers registered yet.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Contact Person</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Address</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {suppliers.map((supplier) => (
                                <tr key={supplier.id}>
                                    <td>{supplier.name}</td>
                                    <td>{supplier.contactPerson}</td>
                                    <td>{supplier.email}</td>
                                    <td>{supplier.phone}</td>
                                    <td>{supplier.address}</td>
                                    <td>
                                        <button onClick={() => handleDelete(supplier.id)}>Delete</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default RegSuppliers
